    def __new__(cls, *tasks, **kwargs):
        # This forces `chain(X, Y, Z)` to work the same way as `X | Y | Z`
        if not kwargs and tasks:
            if len(tasks) != 1 or is_list(tasks[0]):
                tasks = tasks[0] if len(tasks) == 1 else tasks
                return reduce(operator.or_, tasks)
        return super(chain, cls).__new__(cls, *tasks, **kwargs)