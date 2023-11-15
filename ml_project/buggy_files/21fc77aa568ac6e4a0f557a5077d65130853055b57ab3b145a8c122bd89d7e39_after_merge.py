def function_type(func: mypy.nodes.FuncBase, fallback: Instance) -> FunctionLike:
    if func.type:
        assert isinstance(func.type, FunctionLike)
        return func.type
    else:
        # Implicit type signature with dynamic types.
        if isinstance(func, mypy.nodes.FuncItem):
            return callable_type(func, fallback)
        else:
            # Broken overloads can have self.type set to None.
            # TODO: should we instead always set the type in semantic analyzer?
            assert isinstance(func, mypy.nodes.OverloadedFuncDef)
            any_type = AnyType(TypeOfAny.from_error)
            dummy = CallableType([any_type, any_type],
                                 [ARG_STAR, ARG_STAR2],
                                 [None, None], any_type,
                                 fallback,
                                 line=func.line, is_ellipsis_args=True)
            # Return an Overloaded, because some callers may expect that
            # an OverloadedFuncDef has an Overloaded type.
            return Overloaded([dummy])