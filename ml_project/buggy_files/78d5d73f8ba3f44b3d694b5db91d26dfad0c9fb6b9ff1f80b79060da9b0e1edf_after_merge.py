def dependent(func):
    func.is_dependent = True
    func.is_wipe_action = True
    return func