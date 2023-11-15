    def __repr__(self):
        # Calculate a hash that represents most data about the post
        m = hashlib.md5()
        # source_path modification date (to avoid reading it)
        m.update(utils.unicode_str(os.stat(self.source_path).st_mtime).encode('utf-8'))
        clean_meta = {}
        for k, v in self.meta.items():
            sub_meta = {}
            clean_meta[k] = sub_meta
            for kk, vv in v.items():
                if vv:
                    sub_meta[kk] = vv
        m.update(utils.unicode_str(json.dumps(clean_meta, cls=utils.CustomEncoder, sort_keys=True)).encode('utf-8'))
        return '<Post: {0!r} {1}>'.format(self.source_path, m.hexdigest())