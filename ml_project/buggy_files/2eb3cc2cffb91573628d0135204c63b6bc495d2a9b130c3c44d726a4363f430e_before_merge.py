    def login(self, return_to_browser=False):
        """Logon to the server."""
        ret = True

        if not self.args.snmp_force:
            # First of all, trying to connect to a Glances server
            self.set_mode('glances')
            client_version = None
            try:
                client_version = self.client.init()
            except socket.error as err:
                # Fallback to SNMP
                logger.error("Connection to Glances server failed (%s)" % err)
                self.set_mode('snmp')
                fallbackmsg = _("Trying fallback to SNMP...")
                if not return_to_browser:
                    print(fallbackmsg)
                else:
                    logger.info(fallbackmsg)
            except ProtocolError as err:
                # Others errors
                if str(err).find(" 401 ") > 0:
                    msg = "Connection to server failed (bad password)"
                else:
                    msg = "Connection to server failed ({0})".format(err)
                if not return_to_browser:
                    logger.critical(msg)
                    sys.exit(2)
                else:
                    logger.error(msg)
                    return False

            if self.get_mode() == 'glances' and version[:3] == client_version[:3]:
                # Init stats
                self.stats = GlancesStatsClient()
                self.stats.set_plugins(json.loads(self.client.getAllPlugins()))
                logger.debug(
                    "Client version: %s / Server version: %s" % (version, client_version))
            else:
                logger.error(
                    "Client and server not compatible: Client version: %s / Server version: %s" % (version, client_version))

        else:
            self.set_mode('snmp')

        if self.get_mode() == 'snmp':
            logger.info("Trying to grab stats by SNMP...")
            # Fallback to SNMP if needed
            from glances.core.glances_stats import GlancesStatsClientSNMP

            # Init stats
            self.stats = GlancesStatsClientSNMP(args=self.args)

            if not self.stats.check_snmp():
                logger.error("Connection to SNMP server failed")
                if not return_to_browser:
                    sys.exit(2)
                else:
                    return False

        if ret:
            # Load limits from the configuration file
            # Each client can choose its owns limits
            self.stats.load_limits(self.config)

            # Init screen
            self.screen = GlancesCursesClient(args=self.args)

        # Return result
        return ret