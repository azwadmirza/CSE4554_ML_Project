    def load_file(
        self,
        filename: str,
        key: str,
        bucket_name: Optional[str] = None,
        replace: bool = False,
        encrypt: bool = False,
        gzip: bool = False,
        acl_policy: Optional[str] = None,
    ) -> None:
        """
        Loads a local file to S3

        :param filename: name of the file to load.
        :type filename: str
        :param key: S3 key that will point to the file
        :type key: str
        :param bucket_name: Name of the bucket in which to store the file
        :type bucket_name: str
        :param replace: A flag to decide whether or not to overwrite the key
            if it already exists. If replace is False and the key exists, an
            error will be raised.
        :type replace: bool
        :param encrypt: If True, the file will be encrypted on the server-side
            by S3 and will be stored in an encrypted form while at rest in S3.
        :type encrypt: bool
        :param gzip: If True, the file will be compressed locally
        :type gzip: bool
        :param acl_policy: String specifying the canned ACL policy for the file being
            uploaded to the S3 bucket.
        :type acl_policy: str
        """
        if not replace and self.check_for_key(key, bucket_name):
            raise ValueError(f"The key {key} already exists.")

        extra_args = self.extra_args
        if encrypt:
            extra_args['ServerSideEncryption'] = "AES256"
        if gzip:
            with open(filename, 'rb') as f_in:
                filename_gz = f_in.name + '.gz'
                with gz.open(filename_gz, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
                    filename = filename_gz
        if acl_policy:
            extra_args['ACL'] = acl_policy

        client = self.get_conn()
        client.upload_file(filename, bucket_name, key, ExtraArgs=extra_args)