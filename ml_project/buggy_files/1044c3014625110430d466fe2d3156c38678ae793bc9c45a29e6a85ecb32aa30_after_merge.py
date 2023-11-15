    def get_bucket(self, bucket_name, *args, **kwargs):
        bucket_name = s3_listener.normalize_bucket_name(bucket_name)
        if bucket_name == BUCKET_MARKER_LOCAL:
            return None
        return get_bucket_orig(bucket_name, *args, **kwargs)