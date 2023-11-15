    def get_bucket(self, bucket_name, *args, **kwargs):
        bucket_name = s3_listener.normalize_bucket_name(bucket_name)
        return get_bucket_orig(bucket_name, *args, **kwargs)