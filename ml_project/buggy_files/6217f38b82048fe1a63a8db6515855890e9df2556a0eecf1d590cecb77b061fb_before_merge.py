    def visit_func_def(self, defn: FuncDef) -> None:

        phase_info = self.postpone_nested_functions_stack[-1]
        if phase_info != FUNCTION_SECOND_PHASE:
            self.function_stack.append(defn)
            # First phase of analysis for function.
            self.errors.push_function(defn.name())
            if defn.type:
                assert isinstance(defn.type, CallableType)
                self.update_function_type_variables(defn.type, defn)
            self.errors.pop_function()
            self.function_stack.pop()

            defn.is_conditional = self.block_depth[-1] > 0

            # TODO(jukka): Figure out how to share the various cases. It doesn't
            #   make sense to have (almost) duplicate code (here and elsewhere) for
            #   3 cases: module-level, class-level and local names. Maybe implement
            #   a common stack of namespaces. As the 3 kinds of namespaces have
            #   different semantics, this wouldn't always work, but it might still
            #   be a win.
            if self.is_class_scope():
                # Method definition
                defn.info = self.type
                if not defn.is_decorated and not defn.is_overload:
                    if (defn.name() in self.type.names and
                            self.type.names[defn.name()].node != defn):
                        # Redefinition. Conditional redefinition is okay.
                        n = self.type.names[defn.name()].node
                        if not self.set_original_def(n, defn):
                            self.name_already_defined(defn.name(), defn)
                    self.type.names[defn.name()] = SymbolTableNode(MDEF, defn)
                self.prepare_method_signature(defn)
            elif self.is_func_scope():
                # Nested function
                if not defn.is_decorated and not defn.is_overload:
                    if defn.name() in self.locals[-1]:
                        # Redefinition. Conditional redefinition is okay.
                        n = self.locals[-1][defn.name()].node
                        if not self.set_original_def(n, defn):
                            self.name_already_defined(defn.name(), defn)
                    else:
                        self.add_local(defn, defn)
            else:
                # Top-level function
                if not defn.is_decorated and not defn.is_overload:
                    symbol = self.globals.get(defn.name())
                    if isinstance(symbol.node, FuncDef) and symbol.node != defn:
                        # This is redefinition. Conditional redefinition is okay.
                        if not self.set_original_def(symbol.node, defn):
                            # Report error.
                            self.check_no_global(defn.name(), defn, True)
            if phase_info == FUNCTION_FIRST_PHASE_POSTPONE_SECOND:
                # Postpone this function (for the second phase).
                self.postponed_functions_stack[-1].append(defn)
                return
        if phase_info != FUNCTION_FIRST_PHASE_POSTPONE_SECOND:
            # Second phase of analysis for function.
            self.errors.push_function(defn.name())
            self.analyze_function(defn)
            if defn.is_coroutine and isinstance(defn.type, CallableType):
                if defn.is_async_generator:
                    # Async generator types are handled elsewhere
                    pass
                else:
                    # A coroutine defined as `async def foo(...) -> T: ...`
                    # has external return type `Awaitable[T]`.
                    defn.type = defn.type.copy_modified(
                        ret_type = self.named_type_or_none('typing.Awaitable',
                                                           [defn.type.ret_type]))
            self.errors.pop_function()