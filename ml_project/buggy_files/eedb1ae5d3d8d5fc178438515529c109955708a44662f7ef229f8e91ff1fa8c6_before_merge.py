        def impl(func, iterable):
            for x in iterable:
                if func(x):
                    yield x