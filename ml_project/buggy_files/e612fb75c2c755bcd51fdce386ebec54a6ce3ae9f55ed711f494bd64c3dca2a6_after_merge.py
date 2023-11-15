    def describe_log_groups(self, limit, log_group_name_prefix, next_token):
        if log_group_name_prefix is None:
            log_group_name_prefix = ""

        groups = [
            group.to_describe_dict()
            for name, group in self.groups.items()
            if name.startswith(log_group_name_prefix)
        ]
        groups = sorted(groups, key=lambda x: x["logGroupName"])

        index_start = 0
        if next_token:
            try:
                index_start = (
                    next(
                        index
                        for (index, d) in enumerate(groups)
                        if d["logGroupName"] == next_token
                    )
                    + 1
                )
            except StopIteration:
                index_start = 0
                # AWS returns an empty list if it receives an invalid token.
                groups = []

        index_end = index_start + limit
        if index_end > len(groups):
            index_end = len(groups)

        groups_page = groups[index_start:index_end]

        next_token = None
        if groups_page and index_end < len(groups):
            next_token = groups_page[-1]["logGroupName"]

        return groups_page, next_token