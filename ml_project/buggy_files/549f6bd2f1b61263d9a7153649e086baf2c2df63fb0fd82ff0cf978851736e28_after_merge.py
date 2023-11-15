def notdependent(func):
    func.is_dependent = False
    func.is_wipe_action = True
    return func