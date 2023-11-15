def check_config(config: typing.Dict, required_arguments: typing.List):
    no_arguments = []
    error_arguments = []
    for argument in required_arguments:
        if isinstance(argument, tuple):
            if config.get(argument[0], None) != argument[1]:
                error_arguments.append(argument)
        elif argument not in config:
            no_arguments.append(argument)
    if no_arguments or error_arguments:
        raise Exception('the following arguments are required: {} {}'.format(','.join(no_arguments), ','.join(['{}={}'.format(a[0], a[1]) for a in error_arguments])))