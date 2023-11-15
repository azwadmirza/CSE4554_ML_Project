    def get_result(self):
        highest_type = self._get_highest_type()
        self._check_casts(highest_type)
        return highest_type