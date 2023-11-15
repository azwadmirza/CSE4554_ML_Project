    def _download_folder(self, bucket_name, prefix, target):
        boto_session = self.sagemaker_session.boto_session

        s3 = boto_session.resource('s3')
        bucket = s3.Bucket(bucket_name)

        for obj_sum in bucket.objects.filter(Prefix=prefix):
            obj = s3.Object(obj_sum.bucket_name, obj_sum.key)
            s3_relative_path = obj_sum.key[len(prefix):].lstrip('/')
            file_path = os.path.join(target, s3_relative_path)

            try:
                os.makedirs(os.path.dirname(file_path))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise
                pass
            obj.download_file(file_path)