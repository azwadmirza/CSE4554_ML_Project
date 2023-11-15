    def _upload_file_obj(
        self,
        file_obj: BytesIO,
        key: str,
        bucket_name: Optional[str] = None,
        replace: bool = False,
        encrypt: bool = False,
        acl_policy: Optional[str] = None,
    ) -> None:
        if not replace and self.check_for_key(key, bucket_name):
            raise ValueError(f"The key {key} already exists.")

        extra_args = self.extra_args
        if encrypt:
            extra_args['ServerSideEncryption'] = "AES256"
        if acl_policy:
            extra_args['ACL'] = acl_policy

        client = self.get_conn()
        client.upload_fileobj(
            file_obj,
            bucket_name,
            key,
            ExtraArgs=extra_args,
            Config=self.transfer_config,
        )