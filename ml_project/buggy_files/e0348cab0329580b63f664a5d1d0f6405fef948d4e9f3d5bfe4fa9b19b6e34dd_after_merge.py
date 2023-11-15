    def analyze_overloaded_func_def(self, defn: OverloadedFuncDef) -> None:
        # OverloadedFuncDef refers to any legitimate situation where you have
        # more than one declaration for the same function in a row.  This occurs
        # with a @property with a setter or a deleter, and for a classic
        # @overload.

        defn._fullname = self.qualified_name(defn.name())
        # TODO: avoid modifying items.
        defn.items = defn.unanalyzed_items.copy()

        first_item = defn.items[0]
        first_item.is_overload = True
        first_item.accept(self)

        if isinstance(first_item, Decorator) and first_item.func.is_property:
            # This is a property.
            first_item.func.is_overload = True
            self.analyze_property_with_multi_part_definition(defn)
            typ = function_type(first_item.func, self.builtin_type('builtins.function'))
            assert isinstance(typ, CallableType)
            types = [typ]
        else:
            # This is an a normal overload. Find the item signatures, the
            # implementation (if outside a stub), and any missing @overload
            # decorators.
            types, impl, non_overload_indexes = self.analyze_overload_sigs_and_impl(defn)
            defn.impl = impl
            if non_overload_indexes:
                self.handle_missing_overload_decorators(defn, non_overload_indexes,
                                                        some_overload_decorators=len(types) > 0)
            # If we found an implementation, remove it from the overload item list,
            # as it's special.
            if impl is not None:
                assert impl is defn.items[-1]
                defn.items = defn.items[:-1]
            elif not non_overload_indexes:
                self.handle_missing_overload_implementation(defn)

        if types:
            defn.type = Overloaded(types)
            defn.type.line = defn.line

        if not defn.items:
            # It was not a real overload after all, but function redefinition. We've
            # visited the redefinition(s) already.
            if not defn.impl:
                # For really broken overloads with no items and no implementation we need to keep
                # at least one item to hold basic information like function name.
                defn.impl = defn.unanalyzed_items[-1]
            return

        # We know this is an overload def. Infer properties and perform some checks.
        self.process_final_in_overload(defn)
        self.process_static_or_class_method_in_overload(defn)