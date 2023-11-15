    def infer_function_type_arguments_pass2(
            self, callee_type: CallableType,
            args: List[Node],
            arg_kinds: List[int],
            formal_to_actual: List[List[int]],
            inferred_args: List[Type],
            context: Context) -> Tuple[CallableType, List[Type]]:
        """Perform second pass of generic function type argument inference.

        The second pass is needed for arguments with types such as Callable[[T], S],
        where both T and S are type variables, when the actual argument is a
        lambda with inferred types.  The idea is to infer the type variable T
        in the first pass (based on the types of other arguments).  This lets
        us infer the argument and return type of the lambda expression and
        thus also the type variable S in this second pass.

        Return (the callee with type vars applied, inferred actual arg types).
        """
        # None or erased types in inferred types mean that there was not enough
        # information to infer the argument. Replace them with None values so
        # that they are not applied yet below.
        for i, arg in enumerate(inferred_args):
            if isinstance(arg, NoneTyp) or isinstance(arg, ErasedType):
                inferred_args[i] = None

        callee_type = cast(CallableType, self.apply_generic_arguments(
            callee_type, inferred_args, context))
        arg_types = self.infer_arg_types_in_context2(
            callee_type, args, arg_kinds, formal_to_actual)

        inferred_args = infer_function_type_arguments(
            callee_type, arg_types, arg_kinds, formal_to_actual)

        return callee_type, inferred_args