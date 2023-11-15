    def infer_arg_types_in_context(self, callee: CallableType,
                                   args: List[Node]) -> List[Type]:
        """Infer argument expression types using a callable type as context.

        For example, if callee argument 2 has type List[int], infer the
        argument expression with List[int] type context.
        """
        # TODO Always called with callee as None, i.e. empty context.
        res = []  # type: List[Type]

        fixed = len(args)
        if callee:
            fixed = min(fixed, callee.max_fixed_args())

        arg_type = None  # type: Type
        ctx = None  # type: Type
        for i, arg in enumerate(args):
            if i < fixed:
                if callee and i < len(callee.arg_types):
                    ctx = callee.arg_types[i]
                arg_type = self.accept(arg, ctx)
            else:
                if callee and callee.is_var_arg:
                    arg_type = self.accept(arg, callee.arg_types[-1])
                else:
                    arg_type = self.accept(arg)
            if isinstance(arg_type, ErasedType):
                res.append(NoneTyp())
            else:
                res.append(arg_type)
        return res