    def update(self):
        """Update the stats."""
        if batinfo_tag:
            # Use the batinfo lib to grab the stats
            # Compatible with multiple batteries
            self.bat.update()
            self.bat_list = [{
                'label': 'Battery',
                'value': self.battery_percent,
                'unit': '%'}]
        elif psutil_tag and hasattr(self.bat.sensors_battery(), 'percent'):
            # Use psutil to grab the stats
            # Give directly the battery percent
            self.bat_list = [{
                'label': 'Battery',
                'value': int(self.bat.sensors_battery().percent),
                'unit': '%'}]
        else:
            # No stats...
            self.bat_list = []