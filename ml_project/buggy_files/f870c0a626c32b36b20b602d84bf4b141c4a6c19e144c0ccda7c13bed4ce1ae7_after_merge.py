    def sensors_battery():
        """Return battery info."""
        try:
            percent, minsleft, power_plugged = cext.sensors_battery()
        except NotImplementedError:
            # see: https://github.com/giampaolo/psutil/issues/1074
            return None
        power_plugged = power_plugged == 1
        if power_plugged:
            secsleft = _common.POWER_TIME_UNLIMITED
        elif minsleft == -1:
            secsleft = _common.POWER_TIME_UNKNOWN
        else:
            secsleft = minsleft * 60
        return _common.sbattery(percent, secsleft, power_plugged)