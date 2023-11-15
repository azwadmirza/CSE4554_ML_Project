def step(title):
    if callable(title):
        return StepContext(title.__name__, ({}, {}))(title)
    else:
        return StepContext(title, ({}, {}))