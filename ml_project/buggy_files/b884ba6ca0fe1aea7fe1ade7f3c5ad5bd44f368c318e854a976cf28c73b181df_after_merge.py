    def poll(self):
        try:
            percent = self._get_info()
        except RuntimeError as e:
            return 'Error: {}'.format(e)

        return self.format.format(percent=percent)