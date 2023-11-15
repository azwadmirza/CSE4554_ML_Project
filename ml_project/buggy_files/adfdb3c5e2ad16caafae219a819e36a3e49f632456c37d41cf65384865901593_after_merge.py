    def check_for_missing_annotations(self, fdef: FuncItem) -> None:
        # Check for functions with unspecified/not fully specified types.
        def is_unannotated_any(t: Type) -> bool:
            return isinstance(t, AnyType) and t.type_of_any == TypeOfAny.unannotated

        has_explicit_annotation = (isinstance(fdef.type, CallableType)
                                   and any(not is_unannotated_any(t)
                                           for t in fdef.type.arg_types + [fdef.type.ret_type]))

        show_untyped = not self.is_typeshed_stub or self.options.warn_incomplete_stub
        check_incomplete_defs = self.options.disallow_incomplete_defs and has_explicit_annotation
        if show_untyped and (self.options.disallow_untyped_defs or check_incomplete_defs):
            if fdef.type is None and self.options.disallow_untyped_defs:
                self.fail(messages.FUNCTION_TYPE_EXPECTED, fdef)
            elif isinstance(fdef.type, CallableType):
                ret_type = fdef.type.ret_type
                if is_unannotated_any(ret_type):
                    self.fail(messages.RETURN_TYPE_EXPECTED, fdef)
                elif fdef.is_generator:
                    if is_unannotated_any(self.get_generator_return_type(ret_type,
                                                                        fdef.is_coroutine)):
                        self.fail(messages.RETURN_TYPE_EXPECTED, fdef)
                elif fdef.is_coroutine and isinstance(ret_type, Instance):
                    if is_unannotated_any(self.get_coroutine_return_type(ret_type)):
                        self.fail(messages.RETURN_TYPE_EXPECTED, fdef)
                if any(is_unannotated_any(t) for t in fdef.type.arg_types):
                    self.fail(messages.ARGUMENT_TYPE_EXPECTED, fdef)