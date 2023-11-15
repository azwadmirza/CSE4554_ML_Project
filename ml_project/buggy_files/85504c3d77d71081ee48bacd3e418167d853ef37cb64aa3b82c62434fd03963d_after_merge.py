    def update_views(self):
        """Update stats views."""
        # Call the father's method
        super(Plugin, self).update_views()

        # Add specifics informations
        # Alert and log
        if 'used' in self.stats and 'total' in self.stats:
            self.views['used']['decoration'] = self.get_alert_log(self.stats['used'], maximum=self.stats['total'])