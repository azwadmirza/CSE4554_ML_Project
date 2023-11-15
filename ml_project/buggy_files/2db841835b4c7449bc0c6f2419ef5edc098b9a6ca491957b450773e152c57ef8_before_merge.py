    def analyse_type_annotation(self, env, assigned_value=None):
        annotation = self.expr
        base_type = None
        is_ambiguous = False
        explicit_pytype = explicit_ctype = False
        if annotation.is_dict_literal:
            warning(annotation.pos,
                    "Dicts should no longer be used as type annotations. Use 'cython.int' etc. directly.")
            for name, value in annotation.key_value_pairs:
                if not name.is_string_literal:
                    continue
                if name.value in ('type', b'type'):
                    explicit_pytype = True
                    if not explicit_ctype:
                        annotation = value
                elif name.value in ('ctype', b'ctype'):
                    explicit_ctype = True
                    annotation = value
            if explicit_pytype and explicit_ctype:
                warning(annotation.pos, "Duplicate type declarations found in signature annotation")
        arg_type = annotation.analyse_as_type(env)
        if annotation.is_name and not annotation.cython_attribute and annotation.name in ('int', 'long', 'float'):
            # Map builtin numeric Python types to C types in safe cases.
            if assigned_value is not None and arg_type is not None and not arg_type.is_pyobject:
                assigned_type = assigned_value.infer_type(env)
                if assigned_type and assigned_type.is_pyobject:
                    # C type seems unsafe, e.g. due to 'None' default value  => ignore annotation type
                    is_ambiguous = True
                    arg_type = None
            # ignore 'int' and require 'cython.int' to avoid unsafe integer declarations
            if arg_type in (PyrexTypes.c_long_type, PyrexTypes.c_int_type, PyrexTypes.c_float_type):
                arg_type = PyrexTypes.c_double_type if annotation.name == 'float' else py_object_type
        elif arg_type is not None and annotation.is_string_literal:
            warning(annotation.pos,
                    "Strings should no longer be used for type declarations. Use 'cython.int' etc. directly.",
                    level=1)
        if arg_type is not None:
            if explicit_pytype and not explicit_ctype and not arg_type.is_pyobject:
                warning(annotation.pos,
                        "Python type declaration in signature annotation does not refer to a Python type")
            base_type = Nodes.CAnalysedBaseTypeNode(
                annotation.pos, type=arg_type, is_arg=True)
        elif is_ambiguous:
            warning(annotation.pos, "Ambiguous types in annotation, ignoring")
        else:
            warning(annotation.pos, "Unknown type declaration in annotation, ignoring")
        return base_type, arg_type