    def __init__(self):
        """Init sensors stats."""
        # Temperatures
        self.init_temp = False
        self.stemps = {}
        try:
            # psutil>=5.1.0, Linux-only
            self.stemps = psutil.sensors_temperatures()
        except AttributeError:
            logger.debug("Cannot grab temperatures. Platform not supported.")
        else:
            self.init_temp = True

        # Fans
        self.init_fan = False
        self.sfans = {}
        try:
            # psutil>=5.2.0, Linux-only
            self.sfans = psutil.sensors_fans()
        except AttributeError:
            logger.debug("Cannot grab fans speed. Platform not supported.")
        else:
            self.init_fan = True

        # !!! Disable Fan: High CPU consumption with PSUtil 5.2.0 or higher
        # Delete the two followings lines when corrected (https://github.com/giampaolo/psutil/issues/1199)
        self.init_fan = False
        logger.debug("Fan speed sensors disable (see https://github.com/giampaolo/psutil/issues/1199)")

        # Init the stats
        self.reset()