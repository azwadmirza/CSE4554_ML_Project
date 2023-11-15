    def describe_log_groups(self, limit, log_group_name_prefix, next_token):
        if log_group_name_prefix is None:
            log_group_name_prefix = ""
        if next_token is None:
            next_token = 0

        groups = [
            group.to_describe_dict()
            for name, group in self.groups.items()
            if name.startswith(log_group_name_prefix)
        ]
        groups = sorted(groups, key=lambda x: x["creationTime"], reverse=True)
        groups_page = groups[next_token : next_token + limit]

        next_token += limit
        if next_token >= len(groups):
            next_token = None

        return groups_page, next_token