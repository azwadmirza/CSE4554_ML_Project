    def unify(self, typingctx, other):
        """
        Unify this with the *other* Array.
        """
        if (isinstance(other, Array) and other.ndim == self.ndim
            and other.dtype == self.dtype):
            if self.layout == other.layout:
                layout = self.layout
            else:
                layout = 'A'
            readonly = not (self.mutable and other.mutable)
            aligned = self.aligned and other.aligned
            return Array(dtype=self.dtype, ndim=self.ndim, layout=layout,
                         readonly=readonly, aligned=aligned)