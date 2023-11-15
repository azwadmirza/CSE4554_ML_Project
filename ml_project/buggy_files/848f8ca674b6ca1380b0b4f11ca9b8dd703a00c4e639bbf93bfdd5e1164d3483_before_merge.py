    def visit_member_expr(self, expr: MemberExpr) -> None:
        base = expr.expr
        base.accept(self)
        # Bind references to module attributes.
        if isinstance(base, RefExpr) and base.kind == MODULE_REF:
            # This branch handles the case foo.bar where foo is a module.
            # In this case base.node is the module's MypyFile and we look up
            # bar in its namespace.  This must be done for all types of bar.
            file = cast(Optional[MypyFile], base.node)  # can't use isinstance due to issue #2999
            # TODO: Should we actually use this? Not sure if this makes a difference.
            # if file.fullname() == self.cur_mod_id:
            #     names = self.globals
            # else:
            #     names = file.names
            n = file.names.get(expr.name, None) if file is not None else None
            n = self.dereference_module_cross_ref(n)
            if n and not n.module_hidden:
                if not n:
                    return
                n = self.rebind_symbol_table_node(n)
                if n:
                    # TODO: What if None?
                    expr.kind = n.kind
                    expr.fullname = n.fullname
                    expr.node = n.node
            elif (file is not None and (file.is_stub or self.options.python_version >= (3, 7))
                    and '__getattr__' in file.names):
                # If there is a module-level __getattr__, then any attribute on the module is valid
                # per PEP 484.
                getattr_defn = file.names['__getattr__']
                if not getattr_defn:
                    typ = AnyType(TypeOfAny.from_error)  # type: Type
                elif isinstance(getattr_defn.node, (FuncDef, Var)):
                    if isinstance(getattr_defn.node.type, CallableType):
                        typ = getattr_defn.node.type.ret_type
                    else:
                        typ = AnyType(TypeOfAny.from_error)
                else:
                    typ = AnyType(TypeOfAny.from_error)
                expr.kind = MDEF
                expr.fullname = '{}.{}'.format(file.fullname(), expr.name)
                expr.node = Var(expr.name, type=typ)
            else:
                # We only catch some errors here; the rest will be
                # caught during type checking.
                #
                # This way we can report a larger number of errors in
                # one type checker run. If we reported errors here,
                # the build would terminate after semantic analysis
                # and we wouldn't be able to report any type errors.
                full_name = '%s.%s' % (file.fullname() if file is not None else None, expr.name)
                mod_name = " '%s'" % file.fullname() if file is not None else ''
                if full_name in obsolete_name_mapping:
                    self.fail("Module%s has no attribute %r (it's now called %r)" % (
                        mod_name, expr.name, obsolete_name_mapping[full_name]), expr)
        elif isinstance(base, RefExpr):
            # This branch handles the case C.bar (or cls.bar or self.bar inside
            # a classmethod/method), where C is a class and bar is a type
            # definition or a module resulting from `import bar` (or a module
            # assignment) inside class C. We look up bar in the class' TypeInfo
            # namespace.  This is done only when bar is a module or a type;
            # other things (e.g. methods) are handled by other code in
            # checkmember.
            type_info = None
            if isinstance(base.node, TypeInfo):
                # C.bar where C is a class
                type_info = base.node
            elif isinstance(base.node, Var) and self.type and self.function_stack:
                # check for self.bar or cls.bar in method/classmethod
                func_def = self.function_stack[-1]
                if not func_def.is_static and isinstance(func_def.type, CallableType):
                    formal_arg = func_def.type.argument_by_name(base.node.name())
                    if formal_arg and formal_arg.pos == 0:
                        type_info = self.type
            elif isinstance(base.node, TypeAlias) and base.node.no_args:
                if isinstance(base.node.target, Instance):
                    type_info = base.node.target.type

            if type_info:
                n = type_info.names.get(expr.name)
                if n is not None and (n.kind == MODULE_REF or isinstance(n.node, (TypeInfo,
                                                                                  TypeAlias))):
                    if not n:
                        return
                    expr.kind = n.kind
                    expr.fullname = n.fullname
                    expr.node = n.node