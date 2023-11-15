    def get_named_tileable_infos(self, name: str):
        tileable_key = self._meta_api.get_tileable_key_by_name(self._session_id, name)
        nsplits = self.get_tileable_metas([tileable_key], filter_fields=['nsplits'])[0][0]
        shape = tuple(sum(s) for s in nsplits)
        return TileableInfos(tileable_key, shape)