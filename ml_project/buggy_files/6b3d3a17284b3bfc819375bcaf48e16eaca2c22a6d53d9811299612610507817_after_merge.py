    def end_time(self):
        """Return the end time of the object."""
        try:
            # MSG:
            try:
                return datetime.strptime(self.nc.attrs['time_coverage_end'],
                                         '%Y-%m-%dT%H:%M:%SZ')
            except TypeError:
                return datetime.strptime(self.nc.attrs['time_coverage_end'].astype(str),
                                         '%Y-%m-%dT%H:%M:%SZ')
        except ValueError:
            # PPS:
            return datetime.strptime(self.nc.attrs['time_coverage_end'],
                                     '%Y%m%dT%H%M%S%fZ')