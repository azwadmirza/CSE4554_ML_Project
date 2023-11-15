    def declare_from_annotation(self, env, as_target=False):
        """Implements PEP 526 annotation typing in a fairly relaxed way.

        Annotations are ignored for global variables, Python class attributes and already declared variables.
        String literals are allowed and ignored.
        The ambiguous Python types 'int' and 'long' are ignored and the 'cython.int' form must be used instead.
        """
        if not env.directives['annotation_typing']:
            return
        if env.is_module_scope or env.is_py_class_scope:
            # annotations never create global cdef names and Python classes don't support them anyway
            return
        name = self.name
        if self.entry or env.lookup_here(name) is not None:
            # already declared => ignore annotation
            return

        annotation = self.annotation
        if annotation.expr.is_string_literal:
            # name: "description" => not a type, but still a declared variable or attribute
            atype = None
        else:
            _, atype = annotation.analyse_type_annotation(env)
        if atype is None:
            atype = unspecified_type if as_target and env.directives['infer_types'] != False else py_object_type
        if atype.is_fused and env.fused_to_specific:
            atype = atype.specialize(env.fused_to_specific)
        self.entry = env.declare_var(name, atype, self.pos, is_cdef=not as_target)
        self.entry.annotation = annotation.expr