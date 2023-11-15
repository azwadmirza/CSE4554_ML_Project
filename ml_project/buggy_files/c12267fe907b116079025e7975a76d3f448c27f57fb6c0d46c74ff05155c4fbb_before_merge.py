        def patch() -> None:
            # Calculate the correct value type for the fallback Mapping.
            fallback.args[1] = join.join_type_list(types)