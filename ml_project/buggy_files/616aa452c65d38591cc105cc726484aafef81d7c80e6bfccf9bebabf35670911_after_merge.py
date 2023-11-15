def _match_types(arg1, arg2):
    """Convert the numerical argument to the same type as the other argument"""
    def upgrade(arg_number, arg_structure):
        if isinstance(arg_structure, tuple):
            return (arg_number, arg_number)
        elif isinstance(arg_structure, dict):
            arg = copy.deepcopy(arg_structure)
            for k in arg:
                arg[k] = upgrade(arg_number, arg_structure[k])
            return arg
        else:
            return arg_number

    if (isinstance(arg1, float) or isinstance(arg1, int)):
        return upgrade(arg1, arg2), arg2
    elif (isinstance(arg2, float) or isinstance(arg2, int)):
        return arg1, upgrade(arg2, arg1)

    return arg1, arg2