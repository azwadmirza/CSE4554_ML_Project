    def _extractKeyInfoFromUrl(url):
        """
        :return: (bucket, key)
        """
        s3 = boto.connect_s3()
        bucket = s3.get_bucket(url.netloc)
        key = bucket.new_key(url.path[1:])
        return bucket, key