    def from_unpack_list(cls, *args):
        (infohash, name, length, num_files, category_list_str, creation_date, seeders, leechers, cid) = args
        category_list = decode_values(category_list_str)
        return SearchResponseItemPayload(infohash, name, length, num_files, category_list, creation_date, seeders,
                                         leechers, cid)