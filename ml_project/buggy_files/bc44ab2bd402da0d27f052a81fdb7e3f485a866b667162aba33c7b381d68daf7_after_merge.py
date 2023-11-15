    def get_shape_classes(self, var, typemap=None):
        """get the shape classes for a given variable.
        If a typemap is specified then use it for type resolution
        """
        # We get shape classes from the equivalence set but that
        # keeps its own typemap at a time prior to lowering.  So
        # if something is added during lowering then we can pass
        # in a type map to use.  We temporarily replace the
        # equivalence set typemap, do the work and then restore
        # the original on the way out.
        if typemap is not None:
            save_typemap = self.equiv_set.typemap
            self.equiv_set.typemap = typemap
        res = self.equiv_set.get_shape_classes(var)
        if typemap is not None:
            self.equiv_set.typemap = save_typemap
        return res