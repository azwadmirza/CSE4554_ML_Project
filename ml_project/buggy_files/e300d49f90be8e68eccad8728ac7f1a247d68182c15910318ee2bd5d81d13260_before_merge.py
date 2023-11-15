    def visit_func_def(self, defn: FuncDef) -> Type:
        """Type check a function definition."""
        self.check_func_item(defn, name=defn.name())
        if defn.info:
            if not defn.is_dynamic():
                self.check_method_override(defn)
            self.check_inplace_operator_method(defn)
        if defn.original_def:
            # Override previous definition.
            new_type = self.function_type(defn)
            if isinstance(defn.original_def, FuncDef):
                # Function definition overrides function definition.
                if not is_same_type(new_type, self.function_type(defn.original_def)):
                    self.msg.incompatible_conditional_function_def(defn)
            else:
                # Function definition overrides a variable initialized via assignment.
                orig_type = defn.original_def.type
                if isinstance(orig_type, PartialType):
                    if orig_type.type is None:
                        # Ah this is a partial type. Give it the type of the function.
                        defn.original_def.type = new_type
                        partial_types = self.partial_types[-1]
                        del partial_types[defn.original_def]
                    else:
                        # Trying to redefine something like partial empty list as function.
                        self.fail(messages.INCOMPATIBLE_REDEFINITION, defn)
                else:
                    # TODO: Update conditional type binder.
                    self.check_subtype(orig_type, new_type, defn,
                                       messages.INCOMPATIBLE_REDEFINITION,
                                       'original type',
                                       'redefinition with type')