    def __init__(self):
        """Init sensors stats."""
        # Temperatures
        self.init_temp = False
        self.stemps = {}
        try:
            # psutil>=5.1.0 is required
            self.stemps = psutil.sensors_temperatures()
        except AttributeError:
            logger.warning("Temperature sensors are only available on Linux")
            logger.warning("PsUtil 5.1.0 or higher is needed to grab temperatures sensors")
        except OSError as e:
            # FreeBSD: If oid 'hw.acpi.battery' not present, Glances wont start #1055
            logger.error("Can not grab temperatures sensors ({})".format(e))
        else:
            self.init_temp = True

        # Fans
        self.init_fan = False
        self.sfans = {}
        try:
            # psutil>=5.2.0 is required
            self.sfans = psutil.sensors_fans()
        except AttributeError:
            logger.warning("Fan speed sensors are only available on Linux")
            logger.warning("PsUtil 5.2.0 or higher is needed to grab fans sensors")
        except OSError as e:
            logger.error("Can not grab fans sensors ({})".format(e))
        else:
            self.init_fan = True

        # !!! Disable Fan: High CPU consumption with PSUtil 5.2.0 or higher
        # Delete the two followings lines when corrected (https://github.com/giampaolo/psutil/issues/1199)
        self.init_fan = False
        logger.debug("Fan speed sensors disable (see https://github.com/giampaolo/psutil/issues/1199)")

        # Init the stats
        self.reset()