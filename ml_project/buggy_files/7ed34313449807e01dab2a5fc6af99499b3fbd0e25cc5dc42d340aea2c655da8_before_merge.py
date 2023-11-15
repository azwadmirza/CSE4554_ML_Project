    def declare_var(self, name, type, pos,
                    cname = None, visibility = 'private',
                    api = 0, in_pxd = 0, is_cdef = 0):
        name = self.mangle_special_name(name)
        if is_cdef:
            # Add an entry for an attribute.
            if self.defined:
                error(pos,
                    "C attributes cannot be added in implementation part of"
                    " extension type defined in a pxd")
            if not self.is_closure_class_scope and get_special_method_signature(name):
                error(pos,
                    "The name '%s' is reserved for a special method."
                        % name)
            if not cname:
                cname = name
                if visibility == 'private':
                    cname = c_safe_identifier(cname)
                cname = punycodify_name(cname, Naming.unicode_structmember_prefix)
            if type.is_cpp_class and visibility != 'extern':
                type.check_nullary_constructor(pos)
                self.use_utility_code(Code.UtilityCode("#include <new>"))
            entry = self.declare(name, cname, type, pos, visibility)
            entry.is_variable = 1
            self.var_entries.append(entry)
            if type.is_memoryviewslice:
                self.has_memoryview_attrs = True
            elif type.is_cpp_class:
                self.has_cpp_class_attrs = True
            elif type.is_pyobject and (self.is_closure_class_scope or name != '__weakref__'):
                self.has_pyobject_attrs = True
                if (not type.is_builtin_type
                        or not type.scope or type.scope.needs_gc()):
                    self.has_cyclic_pyobject_attrs = True
            if visibility not in ('private', 'public', 'readonly'):
                error(pos,
                    "Attribute of extension type cannot be declared %s" % visibility)
            if visibility in ('public', 'readonly'):
                # If the field is an external typedef, we cannot be sure about the type,
                # so do conversion ourself rather than rely on the CPython mechanism (through
                # a property; made in AnalyseDeclarationsTransform).
                entry.needs_property = True
                if not self.is_closure_class_scope and name == "__weakref__":
                    error(pos, "Special attribute __weakref__ cannot be exposed to Python")
                if not (type.is_pyobject or type.can_coerce_to_pyobject(self)):
                    # we're not testing for coercion *from* Python here - that would fail later
                    error(pos, "C attribute of type '%s' cannot be accessed from Python" % type)
            else:
                entry.needs_property = False
            return entry
        else:
            if type is unspecified_type:
                type = py_object_type
            # Add an entry for a class attribute.
            entry = Scope.declare_var(self, name, type, pos,
                                      cname=cname, visibility=visibility,
                                      api=api, in_pxd=in_pxd, is_cdef=is_cdef)
            entry.is_member = 1
            entry.is_pyglobal = 1 # xxx: is_pyglobal changes behaviour in so many places that
                                  # I keep it in for now. is_member should be enough
                                  # later on
            self.namespace_cname = "(PyObject *)%s" % self.parent_type.typeptr_cname

            return entry