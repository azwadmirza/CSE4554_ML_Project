    def get_file_hash(self, path_info):
        import base64
        import codecs

        bucket = path_info.bucket
        path = path_info.path
        blob = self.gs.bucket(bucket).get_blob(path)
        if not blob:
            return HashInfo(self.PARAM_CHECKSUM, None)

        b64_md5 = blob.md5_hash
        md5 = base64.b64decode(b64_md5)
        return HashInfo(
            self.PARAM_CHECKSUM,
            codecs.getencoder("hex")(md5)[0].decode("utf-8"),
        )