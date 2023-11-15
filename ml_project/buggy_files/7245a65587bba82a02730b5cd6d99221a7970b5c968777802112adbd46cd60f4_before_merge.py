    def infer_variable_type(self, name: Var, lvalue: Lvalue,
                            init_type: Type, context: Context) -> None:
        """Infer the type of initialized variables from initializer type."""
        if isinstance(init_type, DeletedType):
            self.msg.deleted_as_rvalue(init_type, context)
        elif not is_valid_inferred_type(init_type):
            # We cannot use the type of the initialization expression for full type
            # inference (it's not specific enough), but we might be able to give
            # partial type which will be made more specific later. A partial type
            # gets generated in assignment like 'x = []' where item type is not known.
            if not self.infer_partial_type(name, lvalue, init_type):
                self.fail(messages.NEED_ANNOTATION_FOR_VAR, context)
                self.set_inference_error_fallback_type(name, lvalue, init_type, context)
        elif (isinstance(lvalue, MemberExpr) and self.inferred_attribute_types is not None
              and lvalue.def_var and lvalue.def_var in self.inferred_attribute_types
              and not is_same_type(self.inferred_attribute_types[lvalue.def_var], init_type)):
            # Multiple, inconsistent types inferred for an attribute.
            self.fail(messages.NEED_ANNOTATION_FOR_VAR, context)
            name.type = AnyType(TypeOfAny.from_error)
        else:
            # Infer type of the target.

            # Make the type more general (strip away function names etc.).
            init_type = strip_type(init_type)

            self.set_inferred_type(name, lvalue, init_type)