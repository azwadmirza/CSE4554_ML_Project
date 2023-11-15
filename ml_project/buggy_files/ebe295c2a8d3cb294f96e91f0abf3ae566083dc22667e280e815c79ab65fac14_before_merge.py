    def _has_full_access_to_all_cloud_apis(self, raw_instance):
        full_access_scope = 'https://www.googleapis.com/auth/cloud-platform'
        return any(
            full_access_scope in service_account['scopes'] for service_account in raw_instance['serviceAccounts'])