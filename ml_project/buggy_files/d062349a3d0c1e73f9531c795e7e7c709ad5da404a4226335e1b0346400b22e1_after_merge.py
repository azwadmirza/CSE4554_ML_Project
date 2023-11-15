    def timezone(self):
        """Get the timezone."""
        res = self.send("get_timezone")[0]
        if isinstance(res, dict):
            # Xiaowa E25 example
            # {'olson': 'Europe/Berlin', 'posix': 'CET-1CEST,M3.5.0,M10.5.0/3'}
            if "olson" not in res:
                raise VacuumException("Unsupported timezone format: %s" % res)

            return res["olson"]

        # Gen1 vacuum: ['Europe/Berlin']
        return res