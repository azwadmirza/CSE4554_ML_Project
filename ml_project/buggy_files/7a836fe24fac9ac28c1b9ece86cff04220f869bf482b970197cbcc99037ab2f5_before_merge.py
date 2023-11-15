    def on_health_response(self, response):
        total_seeders = 0
        total_leechers = 0

        if not response or 'error' in response:
            self.update_health(0, 0)  # Just set the health to 0 seeders, 0 leechers
            return

        for _, status in response['health'].iteritems():
            if 'error' in status:
                continue  # Timeout or invalid status

            total_seeders += int(status['seeders'])
            total_leechers += int(status['leechers'])

        self.is_health_checking = False
        self.update_health(total_seeders, total_leechers)