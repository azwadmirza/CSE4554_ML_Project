    def describe_log_groups(self):
        log_group_name_prefix = self._get_param("logGroupNamePrefix")
        next_token = self._get_param("nextToken")
        limit = self._get_param("limit", 50)
        assert limit <= 50
        groups, next_token = self.logs_backend.describe_log_groups(
            limit, log_group_name_prefix, next_token
        )
        result = {"logGroups": groups}
        if next_token:
            result["nextToken"] = next_token
        return json.dumps(result)