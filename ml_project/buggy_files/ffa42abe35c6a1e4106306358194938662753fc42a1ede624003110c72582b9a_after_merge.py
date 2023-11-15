    def __init__(self):
        """Init sensors stats."""
        # Temperatures
        self.initok = False
        self.stemps = {}
        try:
            # psutil>=5.1.0 is required
            self.stemps = psutil.sensors_temperatures()
        except AttributeError:
            logger.warning("PsUtil 5.1.0 or higher is needed to grab temperatures sensors")
        except OSError as e:
            # FreeBSD: If oid 'hw.acpi.battery' not present, Glances wont start #1055
            logger.error("Can not grab temperatures sensors ({})".format(e))
        else:
            self.initok = True

        # Fans
        self.sfans = {}
        try:
            # psutil>=5.2.0 is required
            self.sfans = psutil.sensors_fans()
        except AttributeError:
            logger.warning("PsUtil 5.2.0 or higher is needed to grab fans sensors")
        except OSError as e:
            logger.error("Can not grab fans sensors ({})".format(e))

        # Init the stats
        self.reset()