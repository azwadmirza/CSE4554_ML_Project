    def analyze_ref_expr(self, e: RefExpr, lvalue: bool = False) -> Type:
        result = None  # type: Type
        node = e.node
        if isinstance(node, Var):
            # Variable reference.
            result = self.analyze_var_ref(node, e)
            if isinstance(result, PartialType):
                if result.type is None:
                    # 'None' partial type. It has a well-defined type. In an lvalue context
                    # we want to preserve the knowledge of it being a partial type.
                    if not lvalue:
                        result = NoneTyp()
                else:
                    partial_types = self.chk.find_partial_types(node)
                    if partial_types is not None:
                        context = partial_types[node]
                        self.msg.fail(messages.NEED_ANNOTATION_FOR_VAR, context)
                    result = AnyType()
        elif isinstance(node, FuncDef):
            # Reference to a global function.
            result = function_type(node, self.named_type('builtins.function'))
        elif isinstance(node, OverloadedFuncDef):
            result = node.type
        elif isinstance(node, TypeInfo):
            # Reference to a type object.
            result = type_object_type(node, self.named_type)
        elif isinstance(node, MypyFile):
            # Reference to a module object.
            result = self.named_type('builtins.module')
        elif isinstance(node, Decorator):
            result = self.analyze_var_ref(node.var, e)
        else:
            # Unknown reference; use any type implicitly to avoid
            # generating extra type errors.
            result = AnyType()
        return result