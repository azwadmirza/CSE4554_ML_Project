    def _extractKeyInfoFromUrl(url, existing=None):
        """
        Extracts bucket and key from URL. The existing parameter determines if a
        particular state of existence should be enforced. Note also that if existing
        is not True and the key does not exist.

        :param existing: determines what the state
        :return: (bucket, key)
        """
        s3 = boto.connect_s3()
        bucket = s3.get_bucket(url.netloc)
        key = bucket.get_key(url.path[1:])

        if existing is True:
            if key is None:
                raise RuntimeError('Key does not exist.')
        elif existing is False:
            if key is not None:
                raise RuntimeError('Key exists.')
        elif existing is None:
            pass
        else:
            assert False

        if key is None:
            key = bucket.new_key(url.path[1:])

        return bucket, key