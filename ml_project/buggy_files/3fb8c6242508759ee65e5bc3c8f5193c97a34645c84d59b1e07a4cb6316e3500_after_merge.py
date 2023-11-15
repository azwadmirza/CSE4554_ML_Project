    def format_multi_opt(valid_type):
        try:
            num_types = len(valid_type)
        except TypeError:
            # Bare type name won't have a length, return the name of the type
            # passed.
            return valid_type.__name__
        else:
            def get_types(types, type_tuple):
                for item in type_tuple:
                    if isinstance(item, tuple):
                        get_types(types, item)
                    else:
                        try:
                            types.append(item.__name__)
                        except AttributeError:
                            log.warning(
                                'Unable to interpret type %s while validating '
                                'configuration', item
                            )
            types = []
            get_types(types, valid_type)

            ret = ', '.join(types[:-1])
            ret += ' or ' + types[-1]
            return ret