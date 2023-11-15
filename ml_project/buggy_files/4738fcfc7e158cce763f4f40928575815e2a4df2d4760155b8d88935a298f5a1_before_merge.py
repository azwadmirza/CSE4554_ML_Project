    def coerce_to_strict(self, const):
        """
        This is used to ultimately *encode* into strict JSON, see `encode`

        """
        # before python 2.7, 'true', 'false', 'null', were include here.
        if const in ('Infinity', '-Infinity', 'NaN'):
            return None
        else:
            return const