    def _visit_func_def(self, defn: FuncDef) -> None:
        phase_info = self.postpone_nested_functions_stack[-1]
        if phase_info != FUNCTION_SECOND_PHASE:
            self.function_stack.append(defn)
            # First phase of analysis for function.
            if not defn._fullname:
                defn._fullname = self.qualified_name(defn.name())
            if defn.type:
                assert isinstance(defn.type, CallableType)
                self.update_function_type_variables(defn.type, defn)
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
                assert self.type is not None, "Type not set at class scope"
                defn.info = self.type
                if not defn.is_decorated and not defn.is_overload:
                    if (defn.name() in self.type.names and
                            self.type.names[defn.name()].node != defn):
                        # Redefinition. Conditional redefinition is okay.
                        n = self.type.names[defn.name()].node
                        if not self.set_original_def(n, defn):
                            self.name_already_defined(defn.name(), defn,
                                                      self.type.names[defn.name()])
                    self.type.names[defn.name()] = SymbolTableNode(MDEF, defn)
                self.prepare_method_signature(defn, self.type)
            elif self.is_func_scope():
                # Nested function
                assert self.locals[-1] is not None, "No locals at function scope"
                if not defn.is_decorated and not defn.is_overload:
                    if defn.name() in self.locals[-1]:
                        # Redefinition. Conditional redefinition is okay.
                        n = self.locals[-1][defn.name()].node
                        if not self.set_original_def(n, defn):
                            self.name_already_defined(defn.name(), defn,
                                                      self.locals[-1][defn.name()])
                    else:
                        self.add_local(defn, defn)
            else:
                # Top-level function
                if not defn.is_decorated and not defn.is_overload:
                    symbol = self.globals[defn.name()]
                    if isinstance(symbol.node, FuncDef) and symbol.node != defn:
                        # This is redefinition. Conditional redefinition is okay.
                        if not self.set_original_def(symbol.node, defn):
                            # Report error.
                            self.check_no_global(defn.name(), defn, True)

            # Analyze function signature and initializers in the first phase
            # (at least this mirrors what happens at runtime).
            with self.tvar_scope_frame(self.tvar_scope.method_frame()):
                if defn.type:
                    self.check_classvar_in_signature(defn.type)
                    assert isinstance(defn.type, CallableType)
                    # Signature must be analyzed in the surrounding scope so that
                    # class-level imported names and type variables are in scope.
                    analyzer = self.type_analyzer()
                    defn.type = analyzer.visit_callable_type(defn.type, nested=False)
                    self.add_type_alias_deps(analyzer.aliases_used)
                    self.check_function_signature(defn)
                    if isinstance(defn, FuncDef):
                        assert isinstance(defn.type, CallableType)
                        defn.type = set_callable_name(defn.type, defn)
                for arg in defn.arguments:
                    if arg.initializer:
                        arg.initializer.accept(self)

            if phase_info == FUNCTION_FIRST_PHASE_POSTPONE_SECOND:
                # Postpone this function (for the second phase).
                self.postponed_functions_stack[-1].append(defn)
                return
        if phase_info != FUNCTION_FIRST_PHASE_POSTPONE_SECOND:
            # Second phase of analysis for function.
            self.analyze_function(defn)
            if defn.is_coroutine and isinstance(defn.type, CallableType):
                if defn.is_async_generator:
                    # Async generator types are handled elsewhere
                    pass
                else:
                    # A coroutine defined as `async def foo(...) -> T: ...`
                    # has external return type `Coroutine[Any, Any, T]`.
                    any_type = AnyType(TypeOfAny.special_form)
                    ret_type = self.named_type_or_none('typing.Coroutine',
                        [any_type, any_type, defn.type.ret_type])
                    assert ret_type is not None, "Internal error: typing.Coroutine not found"
                    defn.type = defn.type.copy_modified(ret_type=ret_type)