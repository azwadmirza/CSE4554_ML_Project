    def do_i_hate_this(cls, task, action_patterns):
        """Process group of patterns (warn or skip) and returns True if
        task is hated and not whitelisted.
        """
        if action_patterns:
            for query_string in action_patterns:
                query = None
                if task.is_album:
                    query = get_query(query_string, Album)
                else:
                    query = get_query(query_string, Item)
                if any(query.match(item) for item in task.items):
                    return True
        return False