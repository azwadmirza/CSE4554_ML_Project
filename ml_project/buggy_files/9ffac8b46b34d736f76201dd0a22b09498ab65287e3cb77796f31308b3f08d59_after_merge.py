    def format_bare(self, typ: Type, verbosity: int = 0) -> str:
        """
        Convert a type to a relatively short string suitable for error messages.

        This method will return an unquoted string.  If a caller doesn't need to
        perform post-processing on the string output, .format should be used
        instead.  (The caller may want to use .quote_type_string after
        processing has happened, to maintain consistent quoting in messages.)
        """
        if isinstance(typ, Instance):
            itype = typ
            # Get the short name of the type.
            if itype.type.fullname() in ('types.ModuleType',
                                         '_importlib_modulespec.ModuleType'):
                # Make some common error messages simpler and tidier.
                return 'Module'
            if verbosity >= 2:
                base_str = itype.type.fullname()
            else:
                base_str = itype.type.name()
            if itype.args == []:
                # No type arguments, just return the type name
                return base_str
            elif itype.type.fullname() == 'builtins.tuple':
                item_type_str = self.format_bare(itype.args[0])
                return 'Tuple[{}, ...]'.format(item_type_str)
            elif itype.type.fullname() in reverse_type_aliases:
                alias = reverse_type_aliases[itype.type.fullname()]
                alias = alias.split('.')[-1]
                items = [self.format_bare(arg) for arg in itype.args]
                return '{}[{}]'.format(alias, ', '.join(items))
            else:
                # There are type arguments. Convert the arguments to strings.
                # If the result is too long, replace arguments with [...].
                a = []  # type: List[str]
                for arg in itype.args:
                    a.append(self.format_bare(arg))
                s = ', '.join(a)
                if len((base_str + s)) < 150:
                    return '{}[{}]'.format(base_str, s)
                else:
                    return '{}[...]'.format(base_str)
        elif isinstance(typ, TypeVarType):
            # This is similar to non-generic instance types.
            return typ.name
        elif isinstance(typ, TupleType):
            # Prefer the name of the fallback class (if not tuple), as it's more informative.
            if typ.fallback.type.fullname() != 'builtins.tuple':
                return self.format_bare(typ.fallback)
            items = []
            for t in typ.items:
                items.append(self.format_bare(t))
            s = 'Tuple[{}]'.format(', '.join(items))
            if len(s) < 400:
                return s
            else:
                return '<tuple: {} items>'.format(len(items))
        elif isinstance(typ, TypedDictType):
            # If the TypedDictType is named, return the name
            if not typ.is_anonymous():
                return self.format_bare(typ.fallback)
            items = []
            for (item_name, item_type) in typ.items.items():
                modifier = '' if item_name in typ.required_keys else '?'
                items.append('{!r}{}: {}'.format(item_name,
                                                 modifier,
                                                 self.format_bare(item_type)))
            s = 'TypedDict({{{}}})'.format(', '.join(items))
            return s
        elif isinstance(typ, UnionType):
            # Only print Unions as Optionals if the Optional wouldn't have to contain another Union
            print_as_optional = (len(typ.items) -
                                 sum(isinstance(t, NoneTyp) for t in typ.items) == 1)
            if print_as_optional:
                rest = [t for t in typ.items if not isinstance(t, NoneTyp)]
                return 'Optional[{}]'.format(self.format_bare(rest[0]))
            else:
                items = []
                for t in typ.items:
                    items.append(self.format_bare(t))
                s = 'Union[{}]'.format(', '.join(items))
                if len(s) < 400:
                    return s
                else:
                    return '<union: {} items>'.format(len(items))
        elif isinstance(typ, NoneTyp):
            return 'None'
        elif isinstance(typ, AnyType):
            return 'Any'
        elif isinstance(typ, DeletedType):
            return '<deleted>'
        elif isinstance(typ, UninhabitedType):
            if typ.is_noreturn:
                return 'NoReturn'
            else:
                return '<nothing>'
        elif isinstance(typ, TypeType):
            return 'Type[{}]'.format(self.format_bare(typ.item, verbosity))
        elif isinstance(typ, ForwardRef):  # may appear in semanal.py
            return self.format_bare(typ.link, verbosity)
        elif isinstance(typ, FunctionLike):
            func = typ
            if func.is_type_obj():
                # The type of a type object type can be derived from the
                # return type (this always works).
                return self.format_bare(
                    TypeType.make_normalized(
                        erase_type(func.items()[0].ret_type)),
                    verbosity)
            elif isinstance(func, CallableType):
                return_type = self.format_bare(func.ret_type)
                if func.is_ellipsis_args:
                    return 'Callable[..., {}]'.format(return_type)
                arg_strings = []
                for arg_name, arg_type, arg_kind in zip(
                        func.arg_names, func.arg_types, func.arg_kinds):
                    if (arg_kind == ARG_POS and arg_name is None
                            or verbosity == 0 and arg_kind in (ARG_POS, ARG_OPT)):

                        arg_strings.append(
                            self.format_bare(
                                arg_type,
                                verbosity = max(verbosity - 1, 0)))
                    else:
                        constructor = ARG_CONSTRUCTOR_NAMES[arg_kind]
                        if arg_kind in (ARG_STAR, ARG_STAR2) or arg_name is None:
                            arg_strings.append("{}({})".format(
                                constructor,
                                self.format_bare(arg_type)))
                        else:
                            arg_strings.append("{}({}, {})".format(
                                constructor,
                                self.format_bare(arg_type),
                                repr(arg_name)))

                return 'Callable[[{}], {}]'.format(", ".join(arg_strings), return_type)
            else:
                # Use a simple representation for function types; proper
                # function types may result in long and difficult-to-read
                # error messages.
                return 'overloaded function'
        elif isinstance(typ, UnboundType):
            return str(typ)
        elif typ is None:
            raise RuntimeError('Type is None')
        else:
            # Default case; we simply have to return something meaningful here.
            return 'object'