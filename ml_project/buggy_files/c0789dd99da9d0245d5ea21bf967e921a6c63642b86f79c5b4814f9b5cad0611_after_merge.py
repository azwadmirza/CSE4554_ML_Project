    def do_mssp(self, option):
        """
        Negotiate all the information.

        Args:
            option (Option): Not used.

        """

        self.mssp_table = {

            # Required fields

            "NAME": settings.SERVERNAME,
            "PLAYERS": self.get_player_count,
            "UPTIME": self.get_uptime,

            "PORT": list(reversed(settings.TELNET_PORTS)),  # most important port should be last in list

            # Evennia auto-filled
            "CRAWL DELAY": "-1",
            "CODEBASE": utils.get_evennia_version(mode='pretty'),
            "FAMILY": "Custom",
            "ANSI": "1",
            "GMCP": "1" if settings.TELNET_OOB_ENABLED else "0",
            "ATCP": "0",
            "MCCP": "1",
            "MCP": "0",
            "MSDP": "1" if settings.TELNET_OOB_ENABLED else "0",
            "MSP": "0",
            "MXP": "1",
            "PUEBLO": "0",
            "SSL": "1" if settings.SSL_ENABLED else "0",
            "UTF-8": "1",
            "ZMP": "0",
            "VT100": "1",
            "XTERM 256 COLORS": "1",
        }

        # update the static table with the custom one
        if MSSPTable_CUSTOM:
            self.mssp_table.update(MSSPTable_CUSTOM)

        varlist = b''
        for variable, value in self.mssp_table.items():
            if callable(value):
                value = value()
            if utils.is_iter(value):
                for partval in value:
                    varlist += (MSSP_VAR + bytes(variable, 'utf-8') +
                                MSSP_VAL + bytes(partval, 'utf-8'))
            else:
                varlist += MSSP_VAR + bytes(variable, 'utf-8') + MSSP_VAL + bytes(value, 'utf-8')

        # send to crawler by subnegotiation
        self.protocol.requestNegotiation(MSSP, varlist)
        self.protocol.handshake_done()