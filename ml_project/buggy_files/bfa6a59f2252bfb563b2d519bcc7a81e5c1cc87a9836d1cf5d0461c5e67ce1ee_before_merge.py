    def build_namedtuple_typeinfo(self, name: str, items: List[str], types: List[Type],
                                  default_items: Dict[str, Expression]) -> TypeInfo:
        strtype = self.str_type()
        basetuple_type = self.named_type('__builtins__.tuple', [AnyType()])
        dictype = (self.named_type_or_none('builtins.dict', [strtype, AnyType()])
                   or self.object_type())
        # Actual signature should return OrderedDict[str, Union[types]]
        ordereddictype = (self.named_type_or_none('builtins.dict', [strtype, AnyType()])
                          or self.object_type())
        # 'builtins.tuple' has only one type parameter, the corresponding type argument
        #  in the fallback instance is a join of all item types.
        fallback = self.named_type('__builtins__.tuple', [join.join_type_list(types)])
        # Note: actual signature should accept an invariant version of Iterable[UnionType[types]].
        # but it can't be expressed. 'new' and 'len' should be callable types.
        iterable_type = self.named_type_or_none('typing.Iterable', [AnyType()])
        function_type = self.named_type('__builtins__.function')

        info = self.basic_new_typeinfo(name, fallback)
        info.is_named_tuple = True
        info.tuple_type = TupleType(types, fallback)

        def add_field(var: Var, is_initialized_in_class: bool = False,
                      is_property: bool = False) -> None:
            var.info = info
            var.is_initialized_in_class = is_initialized_in_class
            var.is_property = is_property
            info.names[var.name()] = SymbolTableNode(MDEF, var)

        vars = [Var(item, typ) for item, typ in zip(items, types)]
        for var in vars:
            add_field(var, is_property=True)

        tuple_of_strings = TupleType([strtype for _ in items], basetuple_type)
        add_field(Var('_fields', tuple_of_strings), is_initialized_in_class=True)
        add_field(Var('_field_types', dictype), is_initialized_in_class=True)
        add_field(Var('_field_defaults', dictype), is_initialized_in_class=True)
        add_field(Var('_source', strtype), is_initialized_in_class=True)

        tvd = TypeVarDef('NT', 1, [], info.tuple_type)
        selftype = TypeVarType(tvd)

        def add_method(funcname: str,
                       ret: Type,
                       args: List[Argument],
                       name: str = None,
                       is_classmethod: bool = False,
                       ) -> None:
            if is_classmethod:
                first = [Argument(Var('cls'), TypeType(selftype), None, ARG_POS)]
            else:
                first = [Argument(Var('self'), selftype, None, ARG_POS)]
            args = first + args

            types = [arg.type_annotation for arg in args]
            items = [arg.variable.name() for arg in args]
            arg_kinds = [arg.kind for arg in args]
            signature = CallableType(types, arg_kinds, items, ret, function_type,
                                     name=name or info.name() + '.' + funcname)
            signature.variables = [tvd]
            func = FuncDef(funcname, args, Block([]), typ=signature)
            func.info = info
            func.is_class = is_classmethod
            if is_classmethod:
                v = Var(funcname, signature)
                v.is_classmethod = True
                v.info = info
                dec = Decorator(func, [NameExpr('classmethod')], v)
                info.names[funcname] = SymbolTableNode(MDEF, dec)
            else:
                info.names[funcname] = SymbolTableNode(MDEF, func)

        add_method('_replace', ret=selftype,
                   args=[Argument(var, var.type, EllipsisExpr(), ARG_NAMED_OPT) for var in vars])

        def make_init_arg(var: Var) -> Argument:
            default = default_items.get(var.name(), None)
            kind = ARG_POS if default is None else ARG_OPT
            return Argument(var, var.type, default, kind)

        add_method('__init__', ret=NoneTyp(), name=info.name(),
                   args=[make_init_arg(var) for var in vars])
        add_method('_asdict', args=[], ret=ordereddictype)
        add_method('_make', ret=selftype, is_classmethod=True,
                   args=[Argument(Var('iterable', iterable_type), iterable_type, None, ARG_POS),
                         Argument(Var('new'), AnyType(), EllipsisExpr(), ARG_NAMED_OPT),
                         Argument(Var('len'), AnyType(), EllipsisExpr(), ARG_NAMED_OPT)])
        return info