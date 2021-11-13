from aiohttp import ClientResponse
from functools import partial
from quart import redirect
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
            image_array = json["products"][0]["localizedProperties"][0]["images"]

            # Filter the list for the object containing the boxart
            dat = (list(filter(lambda i:i["imagePurpose"] == imagePurpose, image_array)))[0]
            
            # Get the  URL, replacing // with https:// for better compatibility
            url = dat["uri"].replace("//", "https://")

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