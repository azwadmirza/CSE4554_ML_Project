    def _getters(cls):
        getters = plugins.item_field_getters()
        getters['singleton'] = lambda i: i.album_id is None
        # Filesize is given in bytes
        getters['filesize'] = lambda i: os.path.getsize(syspath(i.path))
        return getters