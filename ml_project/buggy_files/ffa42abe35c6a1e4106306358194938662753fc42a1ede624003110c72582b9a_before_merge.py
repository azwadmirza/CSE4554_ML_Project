    def __init__(self):
        """Init sensors stats."""
        # Temperatures
        try:
            # psutil>=5.1.0 is required
            self.stemps = psutil.sensors_temperatures()
        except AttributeError:
            logger.warning("PsUtil 5.1.0 or higher is needed to grab temperatures sensors")
            self.initok = False
            self.stemps = {}
        else:
            self.initok = True

        # Fans
        try:
            # psutil>=5.2.0 is required
            self.sfans = psutil.sensors_fans()
        except AttributeError:
            logger.warning("PsUtil 5.2.0 or higher is needed to grab fans sensors")
            self.sfans = {}

        # Init the stats
        self.reset()