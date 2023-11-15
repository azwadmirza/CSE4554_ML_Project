        def tail_parser(tails: str, obj: Any) -> Any:
            """Return method from end of tail.

            :param tails: Tail string
            :param obj: Search tail from this object
            :return last tailed method
            """
            provider_name, method_name = tails.split('.', 1)

            if '.' in method_name:
                raise UnacceptableField()

            attr = getattr(obj, provider_name)
            if attr is not None:
                return getattr(attr, method_name)