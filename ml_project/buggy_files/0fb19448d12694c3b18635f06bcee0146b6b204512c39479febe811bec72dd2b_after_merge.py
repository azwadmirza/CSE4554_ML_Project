    def infer_function_type_arguments_using_context(
            self, callable: CallableType, error_context: Context) -> CallableType:
        """Unify callable return type to type context to infer type vars.

        For example, if the return type is set[t] where 't' is a type variable
        of callable, and if the context is set[int], return callable modified
        by substituting 't' with 'int'.
        """
        ctx = self.type_context[-1]
        if not ctx:
            return callable
        # The return type may have references to type metavariables that
        # we are inferring right now. We must consider them as indeterminate
        # and they are not potential results; thus we replace them with the
        # special ErasedType type. On the other hand, class type variables are
        # valid results.
        erased_ctx = replace_meta_vars(ctx, ErasedType())
        ret_type = callable.ret_type
        if isinstance(ret_type, TypeVarType):
            if ret_type.values or (not isinstance(ctx, Instance) or
                                   not ctx.args):
                # The return type is a type variable. If it has values, we can't easily restrict
                # type inference to conform to the valid values. If it's unrestricted, we could
                # infer a too general type for the type variable if we use context, and this could
                # result in confusing and spurious type errors elsewhere.
                #
                # Give up and just use function arguments for type inference. As an exception,
                # if the context is a generic instance type, actually use it as context, as
                # this *seems* to usually be the reasonable thing to do.
                #
                # See also github issues #462 and #360.
                ret_type = NoneTyp()
        args = infer_type_arguments(callable.type_var_ids(), ret_type, erased_ctx)
        # Only substitute non-Uninhabited and non-erased types.
        new_args = []  # type: List[Optional[Type]]
        for arg in args:
            if has_uninhabited_component(arg) or has_erased_component(arg):
                new_args.append(None)
            else:
                new_args.append(arg)
        return self.apply_generic_arguments(callable, new_args, error_context)