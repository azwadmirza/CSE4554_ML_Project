    def __update__(self):
        """Update the stats."""
        # Reset the list
        self.reset()

        # Only update if --disable-hddtemp is not set
        if self.args is None or self.args.disable_hddtemp:
            return

        # Fetch the data
        # data = ("|/dev/sda|WDC WD2500JS-75MHB0|44|C|"
        #         "|/dev/sdb|WDC WD2500JS-75MHB0|35|C|"
        #         "|/dev/sdc|WDC WD3200AAKS-75B3A0|45|C|"
        #         "|/dev/sdd|WDC WD3200AAKS-75B3A0|45|C|"
        #         "|/dev/sde|WDC WD3200AAKS-75B3A0|43|C|"
        #         "|/dev/sdf|???|ERR|*|"
        #         "|/dev/sdg|HGST HTS541010A9E680|SLP|*|"
        #         "|/dev/sdh|HGST HTS541010A9E680|UNK|*|")
        data = self.fetch()

        # Exit if no data
        if data == "":
            return

        # Safety check to avoid malformed data
        # Considering the size of "|/dev/sda||0||" as the minimum
        if len(data) < 14:
            data = self.cache if len(self.cache) > 0 else self.fetch()
        self.cache = data

        try:
            fields = data.split(b'|')
        except TypeError:
            fields = ""
        devices = (len(fields) - 1) // 5
        for item in range(devices):
            offset = item * 5
            hddtemp_current = {}
            device = os.path.basename(nativestr(fields[offset + 1]))
            temperature = fields[offset + 3]
            unit = nativestr(fields[offset + 4])
            hddtemp_current['label'] = device
            try:
                hddtemp_current['value'] = float(temperature)
            except ValueError:
                # Temperature could be 'ERR', 'SLP' or 'UNK' (see issue #824)
                hddtemp_current['value'] = temperature
            hddtemp_current['unit'] = unit
            self.hddtemp_list.append(hddtemp_current)