        def _post_request():
            return self.session.post_data(self._mkurl(cmd, *args), data=data)