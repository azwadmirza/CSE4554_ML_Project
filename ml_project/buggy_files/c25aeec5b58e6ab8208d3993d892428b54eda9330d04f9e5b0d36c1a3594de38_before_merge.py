    def update(self):
        """Update sensors stats using the input method."""
        # Reset the stats
        self.reset()

        if self.get_input() == 'local':
            # Update stats using the standard system lib
            self.stats = self.__set_type(self.glancesgrabsensors.get(), 'temperature_core')
            # Append HDD temperature
            hddtemp = self.__set_type(self.hddtemp_plugin.update(), 'temperature_hdd')
            self.stats.extend(hddtemp)
            # Append Batteries %
            batpercent = self.__set_type(self.batpercent_plugin.update(), 'battery')
            self.stats.extend(batpercent)
        elif self.get_input() == 'snmp':
            # Update stats using SNMP
            # No standard: http://www.net-snmp.org/wiki/index.php/Net-SNMP_and_lm-sensors_on_Ubuntu_10.04
            pass

        return self.stats