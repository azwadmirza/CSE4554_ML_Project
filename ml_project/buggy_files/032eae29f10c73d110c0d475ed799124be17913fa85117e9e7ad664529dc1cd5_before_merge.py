    def group_fields(self, fields: List[EmbedField], max_chars=1000):
        curr_group = []
        ret = []
        for f in fields:
            curr_group.append(f)
            if sum(len(f.value) for f in curr_group) > max_chars:
                ret.append(curr_group)
                curr_group = []

        if len(curr_group) > 0:
            ret.append(curr_group)

        return ret