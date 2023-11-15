    def get_shape_classes(self, name):
        """Instead of the shape tuple, return tuple of int, where
        each int is the corresponding class index of the size object.
        Unknown shapes are given class index -1. Return empty tuple
        if the input name is a scalar variable.
        """
        if isinstance(name, ir.Var):
            name = name.name
        typ = self.typemap[name] if name in self.typemap else None
        if not (isinstance(typ, types.BaseTuple) or
                isinstance(typ, types.SliceType) or
                isinstance(typ, types.ArrayCompatible)):
            return []
        names = self._get_names(name)
        inds = tuple(self._get_ind(name) for name in names)
        return inds