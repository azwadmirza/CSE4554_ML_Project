    def __new__(cls, *tasks, **kwargs):
        # This forces `chain(X, Y, Z)` to work the same way as `X | Y | Z`
        if not kwargs and tasks:
            if len(tasks) == 1 and is_list(tasks[0]):
                # ensure chain(generator_expression) works.
                tasks = tasks[0]
            return reduce(operator.or_, tasks)
        return super(chain, cls).__new__(cls, *tasks, **kwargs)