    def start_time(self):
        """Return the start time of the object."""
        try:
            # MSG:
            try:
                return datetime.strptime(self.nc.attrs['time_coverage_start'],
                                         '%Y-%m-%dT%H:%M:%SZ')
            except TypeError:
                return datetime.strptime(self.nc.attrs['time_coverage_start'].astype(str),
                                         '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            # PPS:
            return datetime.strptime(self.nc.attrs['time_coverage_start'],
                                     '%Y%m%dT%H%M%S%fZ')