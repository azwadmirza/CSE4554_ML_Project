    def _result_name(self, other=None):
        # these names are used to index a dimension, so we don't want to
        # preserve them
        name_is_dim = self.name in self.dims
        # use the same naming heuristics as pandas:
        # https://github.com/ContinuumIO/blaze/issues/458#issuecomment-51936356
        ambiguous = (other is not None and hasattr(other, 'name')
                     and other.name != self.name)
        return None if name_is_dim or ambiguous else self.name