    def update(self):
        """Update sensors stats using the input method."""
        # Reset the stats
        self.reset()

        if self.get_input() == 'local':
            # Update stats using the dedicated lib
            try:
                self.stats = self.__set_type(self.glancesgrabsensors.get(), 
                                             'temperature_core')
            except:
                pass
            # Update HDDtemp stats
            try:
                hddtemp = self.__set_type(self.hddtemp_plugin.update(), 
                                          'temperature_hdd')
            except:
                pass
            else:
                # Append HDD temperature
                self.stats.extend(hddtemp)
            # Update batteries stats
            try:
                batpercent = self.__set_type(self.batpercent_plugin.update(), 
                                             'battery')
            except:
                pass
            else:
                # Append Batteries %
                self.stats.extend(batpercent)
        elif self.get_input() == 'snmp':
            # Update stats using SNMP
            # No standard: http://www.net-snmp.org/wiki/index.php/Net-SNMP_and_lm-sensors_on_Ubuntu_10.04
            pass

        return self.stats