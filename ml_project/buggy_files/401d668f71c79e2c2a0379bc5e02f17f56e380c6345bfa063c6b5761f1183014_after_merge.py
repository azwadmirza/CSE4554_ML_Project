    def _get_names(self, obj):
        """Return a set of names for the given obj, where array and tuples
        are broken down to their individual shapes or elements. This is
        safe because both Numba array shapes and Python tuples are immutable.
        """
        if isinstance(obj, ir.Var) or isinstance(obj, str):
            name = obj if isinstance(obj, str) else obj.name
            typ = self.typemap[name]
            if (isinstance(typ, types.BaseTuple) or
                    isinstance(typ, types.ArrayCompatible)):
                ndim = (typ.ndim if isinstance(typ, types.ArrayCompatible)
                        else len(typ))
                # Treat 0d array as if it were a scalar.
                if ndim == 0:
                    return (name,)
                else:
                    return tuple("{}#{}".format(name, i) for i in range(ndim))
            else:
                return (name,)
        elif isinstance(obj, ir.Const):
            if isinstance(obj.value, tuple):
                return obj.value
            else:
                return (obj.value,)
        elif isinstance(obj, tuple):
            return tuple(self._get_names(x)[0] for x in obj)
        elif isinstance(obj, int):
            return (obj,)
        else:
            raise NotImplementedError(
                "ShapeEquivSet does not support {}".format(obj))