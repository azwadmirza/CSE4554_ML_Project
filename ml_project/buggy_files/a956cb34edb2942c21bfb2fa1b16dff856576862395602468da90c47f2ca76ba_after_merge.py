    def align_argument_type(self, env, arg):
        # @cython.locals()
        directive_locals = self.directive_locals
        orig_type = arg.type
        if arg.name in directive_locals:
            type_node = directive_locals[arg.name]
            other_type = type_node.analyse_as_type(env)
        elif isinstance(arg, CArgDeclNode) and arg.annotation and env.directives['annotation_typing']:
            type_node = arg.annotation
            other_type = arg.inject_type_from_annotations(env)
            if other_type is None:
                return arg
        else:
            return arg
        if other_type is None:
            error(type_node.pos, "Not a type")
        elif orig_type is not py_object_type and not orig_type.same_as(other_type):
            error(arg.base_type.pos, "Signature does not agree with previous declaration")
            error(type_node.pos, "Previous declaration here")
        else:
            arg.type = other_type
        return arg