    def post(self, pack_search_request):
        if hasattr(pack_search_request, 'query'):
            packs = packs_service.search_pack_index(pack_search_request.query,
                                                    case_sensitive=False)
            return [PackAPI(**pack) for pack in packs]
        else:
            pack = packs_service.get_pack_from_index(pack_search_request.pack)
            return PackAPI(**pack) if pack else []