    def poll(self):
        try:
            info = self._get_info()
        except RuntimeError as e:
            return 'Error: {}'.format(e)

        percent = info['brightness'] / info['max']
        return self.format.format(percent=percent)