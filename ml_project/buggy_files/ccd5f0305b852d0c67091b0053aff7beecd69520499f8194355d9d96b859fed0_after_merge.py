            def map_func(left, right=right, kwargs=kwargs):
                return pandas.merge(left, right, **kwargs)