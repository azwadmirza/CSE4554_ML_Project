    def declare_var(self, name, type, pos,
                    cname = None, visibility = 'private',
                    api = 0, in_pxd = 0, is_cdef = 0):
        name = self.mangle_special_name(name)
        if type is unspecified_type:
            type = py_object_type
        # Add an entry for a class attribute.
        entry = Scope.declare_var(self, name, type, pos,
                                  cname=cname, visibility=visibility,
                                  api=api, in_pxd=in_pxd, is_cdef=is_cdef)
        entry.is_pyglobal = 1
        entry.is_pyclass_attr = 1
        return entry