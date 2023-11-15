    def _getters(cls):
        getters = plugins.item_field_getters()
        getters['singleton'] = lambda i: i.album_id is None
        getters['filesize'] = Item.try_filesize  # In bytes.
        return getters