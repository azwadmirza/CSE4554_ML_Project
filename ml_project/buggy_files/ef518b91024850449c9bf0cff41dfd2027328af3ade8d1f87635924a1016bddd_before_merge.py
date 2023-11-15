    def is_in_obj(gpr) -> bool:
        if not hasattr(gpr, "name"):
            return False
        try:
            return gpr is obj[gpr.name]
        except (KeyError, IndexError, ValueError):
            # TODO: ValueError: Given date string not likely a datetime.
            # should be KeyError?
            return False