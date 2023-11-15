    def _result_name(self, other=None):

        if self.name in self.dims:
            # these names match dimension, so if we preserve them we will also
            # rename indexes
            return None

        if other is None:
            # shortcut
            return self.name

        other_name = getattr(other, 'name', UNNAMED)
        other_dims = getattr(other, 'dims', ())

        if other_name in other_dims:
            # same trouble as above
            return None

        # use the same naming heuristics as pandas:
        # https://github.com/ContinuumIO/blaze/issues/458#issuecomment-51936356
        if other_name is UNNAMED or other_name == self.name:
            return self.name

        return None