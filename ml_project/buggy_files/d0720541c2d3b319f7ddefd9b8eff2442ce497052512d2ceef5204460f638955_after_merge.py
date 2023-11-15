    def visit_FuncDefNode(self, node):
        """
        Analyse a function and its body, as that hasn't happened yet.  Also
        analyse the directive_locals set by @cython.locals().

        Then, if we are a function with fused arguments, replace the function
        (after it has declared itself in the symbol table!) with a
        FusedCFuncDefNode, and analyse its children (which are in turn normal
        functions). If we're a normal function, just analyse the body of the
        function.
        """
        env = self.current_env()

        self.seen_vars_stack.append(set())
        lenv = node.local_scope
        node.declare_arguments(lenv)

        # @cython.locals(...)
        for var, type_node in node.directive_locals.items():
            if not lenv.lookup_here(var):   # don't redeclare args
                type = type_node.analyse_as_type(lenv)
                if type and type.is_fused and lenv.fused_to_specific:
                    type = type.specialize(lenv.fused_to_specific)
                if type:
                    lenv.declare_var(var, type, type_node.pos)
                else:
                    error(type_node.pos, "Not a type")

        if self._handle_fused(node):
            node = self._create_fused_function(env, node)
        else:
            node.body.analyse_declarations(lenv)
            self._handle_nogil_cleanup(lenv, node)
            self._super_visit_FuncDefNode(node)

        self.seen_vars_stack.pop()
        return node