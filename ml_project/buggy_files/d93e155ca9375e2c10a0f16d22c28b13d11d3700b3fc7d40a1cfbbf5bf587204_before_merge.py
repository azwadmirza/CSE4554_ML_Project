    def _parse_bucket(self, raw_bucket):
        bucket_dict = {}
        bucket_dict['id'] = get_non_provider_id(raw_bucket.id)
        bucket_dict['name'] = raw_bucket.name
        bucket_dict['project_id'] = self.project_id
        bucket_dict['project_number'] = raw_bucket.project_number
        bucket_dict['creation_date'] = raw_bucket.time_created
        bucket_dict['location'] = raw_bucket.location
        bucket_dict['storage_class'] = raw_bucket.storage_class.lower()
        bucket_dict['versioning_enabled'] = raw_bucket.versioning_enabled
        bucket_dict['logging_enabled'] = raw_bucket.logging is not None
        iam_configuration = raw_bucket.iam_configuration.get('uniformBucketLevelAccess', False) or raw_bucket.iam_configuration.get('bucketPolicyOnly', False)
        if iam_configuration:
            bucket_dict['uniform_bucket_level_access'] = policy.get("enabled", False)
        else:
            print("raw_bucket.iam_configuration missing both uniformBucketLevelAccess and bucketPolicyOnly")
            raise 
        
        if bucket_dict['uniform_bucket_level_access']:
            bucket_dict['acls'] = []
            bucket_dict['default_object_acl'] = []
        else:
            bucket_dict['acls'] = list(raw_bucket.acl)
            bucket_dict['default_object_acl'] = list(raw_bucket.default_object_acl)
        
        bucket_dict['acl_configuration'] = self._get_cloudstorage_bucket_acl(raw_bucket)  # FIXME this should be "IAM"
        return bucket_dict['id'], bucket_dict