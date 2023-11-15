    def start_time(self):
        try:
            # MSG:
            return datetime.strptime(self.nc.attrs['time_coverage_start'], '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            # PPS:
            return datetime.strptime(self.nc.attrs['time_coverage_start'], '%Y%m%dT%H%M%S%fZ')