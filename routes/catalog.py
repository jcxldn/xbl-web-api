from aiohttp import ClientResponse
from functools import partial
from quart import Response, redirect
from providers.BlueprintProvider import BlueprintProvider
from providers.LoopbackRequestProvider import LoopbackRequestProvider
from xbox.webapi.api.provider.catalog.models import AlternateIdType, FieldsTemplate

class Catalog(BlueprintProvider, LoopbackRequestProvider):
    async def __get_product_from_alt_id(self, id, type: AlternateIdType, fields: FieldsTemplate):
        return await self.xbl_client.catalog.get_product_from_alternate_id(id, type, fields)

    async def __boxart_callback_on_product_lookup_finish(self, imagePurpose: str, lookupRes: ClientResponse):
        # Check status code
        if (lookupRes.status == 200):
            # Get JSON data
            json = await lookupRes.json()

            # Get image array
            image_array = []
            try:
                image_array = json["products"][0]["localizedProperties"][0]["images"]
            except IndexError:
                res = Response("No images available")
                res.status_code = 404
                return res

            dat = ""

            try:
                # Filter the list for the object containing the boxart
                dat = (list(filter(lambda i:i["imagePurpose"] == imagePurpose, image_array)))[0]
            except IndexError:
                # title does not have the appropiate imagePurpose - let's try and find a substitute!
                try:
                    # BoxArt -> Poster
                    if (imagePurpose == "BoxArt"):
                        # Try "Poster"
                        dat = (list(filter(lambda i:i["imagePurpose"] == "Poster", image_array)))[0]
                    # KeyArt -> Tile
                    if (imagePurpose == "BrandedKeyArt"):
                        tileList = (list(filter(lambda i:i["imagePurpose"] == "Tile", image_array)))
                        # Get the tile image with the largest size
                        # Define the sorter
                        def sorter(i):
                            return i["fileSizeInBytes"]
                        # Sort the list
                        tileList.sort(key=sorter, reverse=True)
                        # Set the output as the largest tile image
                        dat = tileList[0]
                except IndexError:
                    # Can't find anything!
                    # Either Poster/Tile don't exist or it's something like Minecraft Bedrock UWP which returns no results here.
                    # Let's just return a 404.
                    res = Response("Could not find specified image")
                    res.status_code = 404
                    return res
            
            # If we get here, we've found some kind of image!!

            # Get the  URL, replacing // with https:// for better compatibility
            # Only replace it if uri starts with "//"
            url = dat["uri"].replace("//", "https://") if dat["uri"].startswith("//") else dat["uri"]

            # Create a 302 (Found) response
            return redirect(url, code=302)

    async def __boxart_make_loopback_request(self, image, lookupType, id):
        def imageTypes(x):
            return {
                "boxart": "BoxArt",
                "keyart": "BrandedKeyArt"
            }[x]
        
        # convert image purpose into the exact key that the API uses
        imagePurpose = imageTypes(image)
        # Make the request, using functools.partial to pass the imagePurpose through to the callback
        return await self.get("http://localhost:%i/catalog/lookup/%s/%s/browse" % (self.xbl_client._xbl_web_api_current_port, lookupType, id), partial(self.__boxart_callback_on_product_lookup_finish, imagePurpose))

    def routes(self):
        # ---------- Lookup via bigID (store ID) ----------
        # bigID is used for MS Store // Xbox.com store links.
        # TODO: add batch route for this
        @self.openXboxRoute("/lookup/bigid/<id>/<any(browse, details):fields>")
        async def lookup_bigid(id, fields):
            fieldsEnum = FieldsTemplate.BROWSE if fields == "browse" else FieldsTemplate.DETAILS
            return await self.xbl_client.catalog.get_products([id], fieldsEnum)
        
        # ---------- ALTERNATE lookup via pid / titleid/ pfn ----------
        @self.openXboxRoute("/lookup/legacyproductid/<int:id>/<any(browse, details):fields>")
        async def lookup_alternateid_legacy(id, fields):
            fieldsEnum = FieldsTemplate.BROWSE if fields == "browse" else FieldsTemplate.DETAILS
            return await self.__get_product_from_alt_id(id, AlternateIdType.LEGACY_XBOX_PRODUCT_ID, fieldsEnum)
        
        @self.openXboxRoute("/lookup/titleid/<int:id>/<any(browse, details):fields>")
        async def lookup_alternateid_titleid(id, fields):
            fieldsEnum = FieldsTemplate.BROWSE if fields == "browse" else FieldsTemplate.DETAILS
            return await self.__get_product_from_alt_id(id, AlternateIdType.XBOX_TITLE_ID, fieldsEnum)
        
        @self.openXboxRoute("/lookup/pfn/<id>/<any(browse, details):fields>")
        async def lookup_alternateid_pfn(id, fields):
            # pfn: ProductFamilyName (shorthand often used my microsoft)
            fieldsEnum = FieldsTemplate.BROWSE if fields == "browse" else FieldsTemplate.DETAILS
            return await self.__get_product_from_alt_id(id, AlternateIdType.PACKAGE_FAMILY_NAME, fieldsEnum)
        
        # ---------- Shortcut routes to get various images (eg. boxart, keyart, etc) ----------
        # Using loopback requests to above routes - See xuid.py#L34
        # Callback defined above outside of routes()
        @self.xbl_decorator.cachedRoute("/img/<any(boxart, keyart):image>/<any(bigid, legacyproductid, titleid, pfn):lookupType>/<id>")
        async def boxart(image, lookupType, id):
            return await self.__boxart_make_loopback_request(image, lookupType, id)