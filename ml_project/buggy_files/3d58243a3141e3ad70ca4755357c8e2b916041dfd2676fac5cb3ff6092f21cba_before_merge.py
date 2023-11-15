def __virtual__():
    '''
    Only load the module if SenseHat is available
    '''
    if has_sense_hat:
        rotation = __salt__['pillar.get']('sensehat:rotation', 0)
        if rotation in [0, 90, 180, 270]:
            _sensehat.set_rotation(rotation, False)
        else:
            log.error("{0} is not a valid rotation. Using default rotation.".format(rotation))
        return True
    else:
        return False, "The SenseHat excecution module can not be loaded: SenseHat unavailable.\nThis module can only be used on a Raspberry Pi with a SenseHat. Also make sure that the sense_hat python library is installed!"