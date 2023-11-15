    def stage_in_s3(self, taskcat_cfg):
        """
        Upload templates and other artifacts to s3.

        This function creates the s3 bucket with name provided in the config yml file. If
        no bucket name provided, it creates the s3 bucket using project name provided in
        config yml file. And uploads the templates and other artifacts to the s3 bucket.

        :param taskcat_cfg: Taskcat configuration provided in yml file

        """
        if self.public_s3_bucket:
            bucket_or_object_acl = 'public-read'
        else:
            bucket_or_object_acl = 'bucket-owner-read'
        s3_client = self._boto_client.get('s3', region=self.get_default_region(), s3v4=True)
        self.set_project(taskcat_cfg['global']['qsname'])

        if 's3bucket' in taskcat_cfg['global'].keys():
            self.set_s3bucket(taskcat_cfg['global']['s3bucket'])
            self.set_s3bucket_type('defined')
            print(PrintMsg.INFO + "Staging Bucket => " + self.get_s3bucket())
            if len(self.get_s3bucket()) > self._max_bucket_name_length:
                raise TaskCatException("The bucket name you provided is greater than 63 characters.")
        else:
            auto_bucket = 'taskcat-' + self.stack_prefix + '-' + self.get_project() + "-" + jobid[:8]
            auto_bucket = auto_bucket.lower()
            if len(auto_bucket) > self._max_bucket_name_length:
                auto_bucket = auto_bucket[:self._max_bucket_name_length]
            if self.get_default_region():
                print('{0}Creating bucket {1} in {2}'.format(PrintMsg.INFO, auto_bucket, self.get_default_region()))
                if self.get_default_region() == 'us-east-1':
                    response = s3_client.create_bucket(ACL=bucket_or_object_acl,
                                                       Bucket=auto_bucket)
                else:
                    response = s3_client.create_bucket(ACL=bucket_or_object_acl,
                                                       Bucket=auto_bucket,
                                                       CreateBucketConfiguration={
                                                           'LocationConstraint': self.get_default_region()
                                                       })

                self.set_s3bucket_type('auto')
            else:
                raise TaskCatException("Default_region = " + self.get_default_region())

            if response['ResponseMetadata']['HTTPStatusCode'] is 200:
                print(PrintMsg.INFO + "Staging Bucket => [%s]" % auto_bucket)
                self.set_s3bucket(auto_bucket)
            else:
                print('{0}Creating bucket {1} in {2}'.format(PrintMsg.INFO, auto_bucket, self.get_default_region()))
                response = s3_client.create_bucket(ACL=bucket_or_object_acl,
                                                   Bucket=auto_bucket,
                                                   CreateBucketConfiguration={
                                                       'LocationConstraint': self.get_default_region()})

                if response['ResponseMetadata']['HTTPStatusCode'] is 200:
                    print(PrintMsg.INFO + "Staging Bucket => [%s]" % auto_bucket)
                    self.set_s3bucket(auto_bucket)
            if self.tags:
                s3_client.put_bucket_tagging(
                    Bucket=auto_bucket,
                    Tagging={"TagSet": self.tags}
                )

        if os.path.isdir(self.get_project()):
            start_location = "{}/{}".format(".", self.get_project())
        else:
            print('''\t\t Hint: The name specfied as value of qsname ({})
                    must match the root directory of your project'''.format(self.get_project()))
            print("{0}!Cannot find directory [{1}] in {2}".format(PrintMsg.ERROR, self.get_project(), os.getcwd()))
            raise TaskCatException("Please cd to where you project is located")

        S3Sync(s3_client, self.get_s3bucket(), self.get_project(), start_location, bucket_or_object_acl)
        self.s3_url_prefix = "https://" + self.get_s3_hostname() + "/" + self.get_project()
        if self.upload_only:
            exit0("Upload completed successfully")