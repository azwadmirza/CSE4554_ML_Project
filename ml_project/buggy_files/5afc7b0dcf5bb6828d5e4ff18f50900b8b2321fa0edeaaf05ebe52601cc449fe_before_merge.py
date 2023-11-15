    def pred(part):
        # true when slice does *not* reduce
        return isinstance(part, slice) or is_list_like(part)