    def calculate_mro(self) -> None:
        """Calculate and set mro (method resolution order).

        Raise MroError if cannot determine mro.
        """
        mro = linearize_hierarchy(self)
        assert mro, "Could not produce a MRO at all for %s" % (self,)
        self.mro = mro
        self.is_enum = self._calculate_is_enum()
        # The property of falling back to Any is inherited.
        self.fallback_to_any = any(baseinfo.fallback_to_any for baseinfo in self.mro)