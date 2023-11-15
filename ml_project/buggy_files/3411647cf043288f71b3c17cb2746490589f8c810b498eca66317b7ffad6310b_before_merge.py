        def tail_parser(tails: str, obj: Any) -> Any:
            """Return method from end of tail.

            :param tails: Tail string
            :param obj: Search tail from this object
            :return last tailed method
            """
            first, second = tails.split('.', 1)
            if hasattr(obj, first):
                attr = getattr(obj, first)
                if '.' in second:
                    return tail_parser(attr, second)
                else:
                    return getattr(attr, second)