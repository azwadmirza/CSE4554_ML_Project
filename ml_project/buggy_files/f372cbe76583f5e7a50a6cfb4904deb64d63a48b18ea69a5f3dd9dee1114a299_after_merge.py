    def _call_endpoint(self, service, api, json_body):
        db_profile = get_db_profile_from_uri(mlflow.tracking.get_tracking_uri())
        db_creds = get_databricks_host_creds(db_profile)
        endpoint, method = _SERVICE_AND_METHOD_TO_INFO[service][api]
        response_proto = api.Response()
        return call_endpoint(db_creds, endpoint, method, json_body, response_proto)