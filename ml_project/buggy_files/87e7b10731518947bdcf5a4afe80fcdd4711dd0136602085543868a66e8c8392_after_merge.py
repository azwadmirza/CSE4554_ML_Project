    def set(self, key, value):
        key = bytes_to_str(key)
        s3_object = self._get_s3_object(key)
        s3_object.put(Body=value)