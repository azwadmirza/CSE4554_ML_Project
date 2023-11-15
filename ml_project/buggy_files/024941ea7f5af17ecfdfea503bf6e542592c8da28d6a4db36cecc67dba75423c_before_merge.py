    def visit_overloaded_func_def(self, defn: OverloadedFuncDef) -> None:
        # OverloadedFuncDef refers to any legitimate situation where you have
        # more than one declaration for the same function in a row.  This occurs
        # with a @property with a setter or a deleter, and for a classic
        # @overload.

        # Decide whether to analyze this as a property or an overload.  If an
        # overload, and we're outside a stub, find the impl and set it.  Remove
        # the impl from the item list, it's special.
        types = []  # type: List[CallableType]
        non_overload_indexes = []

        # See if the first item is a property (and not an overload)
        first_item = defn.items[0]
        first_item.is_overload = True
        first_item.accept(self)

        if isinstance(first_item, Decorator) and first_item.func.is_property:
            first_item.func.is_overload = True
            self.analyze_property_with_multi_part_definition(defn)
            typ = function_type(first_item.func, self.builtin_type('builtins.function'))
            assert isinstance(typ, CallableType)
            types = [typ]
        else:
            for i, item in enumerate(defn.items):
                if i != 0:
                    # The first item was already visited
                    item.is_overload = True
                    item.accept(self)
                # TODO support decorated overloaded functions properly
                if isinstance(item, Decorator):
                    callable = function_type(item.func, self.builtin_type('builtins.function'))
                    assert isinstance(callable, CallableType)
                    if not any(refers_to_fullname(dec, 'typing.overload')
                               for dec in item.decorators):
                        if i == len(defn.items) - 1 and not self.is_stub_file:
                            # Last item outside a stub is impl
                            defn.impl = item
                        else:
                            # Oops it wasn't an overload after all. A clear error
                            # will vary based on where in the list it is, record
                            # that.
                            non_overload_indexes.append(i)
                    else:
                        item.func.is_overload = True
                        types.append(callable)
                elif isinstance(item, FuncDef):
                    if i == len(defn.items) - 1 and not self.is_stub_file:
                        defn.impl = item
                    else:
                        non_overload_indexes.append(i)
            if non_overload_indexes:
                if types:
                    # Some of them were overloads, but not all.
                    for idx in non_overload_indexes:
                        if self.is_stub_file:
                            self.fail("An implementation for an overloaded function "
                                      "is not allowed in a stub file", defn.items[idx])
                        else:
                            self.fail("The implementation for an overloaded function "
                                      "must come last", defn.items[idx])
                else:
                    for idx in non_overload_indexes[1:]:
                        self.name_already_defined(defn.name(), defn.items[idx])
                    if defn.impl:
                        self.name_already_defined(defn.name(), defn.impl)
                # Remove the non-overloads
                for idx in reversed(non_overload_indexes):
                    del defn.items[idx]
            # If we found an implementation, remove it from the overloads to
            # consider.
            if defn.impl is not None:
                assert defn.impl is defn.items[-1]
                defn.items = defn.items[:-1]

            elif not self.is_stub_file and not non_overload_indexes:
                self.fail(
                    "An overloaded function outside a stub file must have an implementation",
                    defn)

        if types:
            defn.type = Overloaded(types)
            defn.type.line = defn.line

        if self.is_class_scope():
            self.type.names[defn.name()] = SymbolTableNode(MDEF, defn,
                                                           typ=defn.type)
            defn.info = self.type
        elif self.is_func_scope():
            self.add_local(defn, defn)