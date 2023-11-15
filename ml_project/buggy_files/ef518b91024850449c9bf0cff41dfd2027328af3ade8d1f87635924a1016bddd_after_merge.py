    def is_in_obj(gpr) -> bool:
        if not hasattr(gpr, "name"):
            return False
        try:
            return gpr is obj[gpr.name]
        except (KeyError, IndexError):
            # IndexError reached in e.g. test_skip_group_keys when we pass
            #  lambda here
            return False