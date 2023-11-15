    def get_result(self):
        promoted_type = self._get_type()
        return shape_like_args(self.args, promoted_type)