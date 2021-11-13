from providers.BlueprintProvider import BlueprintProvider

from xbox.webapi.api.provider.catalog.models import AlternateIdType, FieldsTemplate

class Catalog(BlueprintProvider):
    async def __get_product_from_alt_id(self, id, type: AlternateIdType, fields: FieldsTemplate):
        return await self.xbl_client.catalog.get_product_from_alternate_id(id, type, fields)

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