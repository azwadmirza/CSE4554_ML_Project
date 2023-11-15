    def check_reverse_op_method(self, defn: FuncItem,
                                reverse_type: CallableType, reverse_name: str,
                                context: Context) -> None:
        """Check a reverse operator method such as __radd__."""
        # Decides whether it's worth calling check_overlapping_op_methods().

        # This used to check for some very obscure scenario.  It now
        # just decides whether it's worth calling
        # check_overlapping_op_methods().

        # First check for a valid signature
        method_type = CallableType([AnyType(TypeOfAny.special_form),
                                    AnyType(TypeOfAny.special_form)],
                                   [nodes.ARG_POS, nodes.ARG_POS],
                                   [None, None],
                                   AnyType(TypeOfAny.special_form),
                                   self.named_type('builtins.function'))
        if not is_subtype(reverse_type, method_type):
            self.msg.invalid_signature(reverse_type, context)
            return

        if reverse_name in ('__eq__', '__ne__'):
            # These are defined for all objects => can't cause trouble.
            return

        # With 'Any' or 'object' return type we are happy, since any possible
        # return value is valid.
        ret_type = reverse_type.ret_type
        if isinstance(ret_type, AnyType):
            return
        if isinstance(ret_type, Instance):
            if ret_type.type.fullname() == 'builtins.object':
                return
        if reverse_type.arg_kinds[0] == ARG_STAR:
            reverse_type = reverse_type.copy_modified(arg_types=[reverse_type.arg_types[0]] * 2,
                                                      arg_kinds=[ARG_POS] * 2,
                                                      arg_names=[reverse_type.arg_names[0], "_"])
        assert len(reverse_type.arg_types) == 2

        forward_name = nodes.normal_from_reverse_op[reverse_name]
        forward_inst = reverse_type.arg_types[1]
        if isinstance(forward_inst, TypeVarType):
            forward_inst = forward_inst.upper_bound
        if isinstance(forward_inst, (FunctionLike, TupleType, TypedDictType)):
            forward_inst = forward_inst.fallback
        if isinstance(forward_inst, TypeType):
            item = forward_inst.item
            if isinstance(item, Instance):
                opt_meta = item.type.metaclass_type
                if opt_meta is not None:
                    forward_inst = opt_meta
        if not (isinstance(forward_inst, (Instance, UnionType))
                and forward_inst.has_readable_member(forward_name)):
            return
        forward_base = reverse_type.arg_types[1]
        forward_type = self.expr_checker.analyze_external_member_access(forward_name, forward_base,
                                                                        context=defn)
        self.check_overlapping_op_methods(reverse_type, reverse_name, defn.info,
                                          forward_type, forward_name, forward_base,
                                          context=defn)