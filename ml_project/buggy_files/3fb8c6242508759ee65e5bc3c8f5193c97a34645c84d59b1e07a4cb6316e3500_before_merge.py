    def format_multi_opt(valid_type):
        try:
            num_types = len(valid_type)
        except TypeError:
            # Bare type name won't have a length, return the name of the type
            # passed.
            return valid_type.__name__
        else:
            if num_types == 1:
                return valid_type.__name__
            elif num_types > 1:
                ret = ', '.join(x.__name__ for x in valid_type[:-1])
                ret += ' or ' + valid_type[-1].__name__