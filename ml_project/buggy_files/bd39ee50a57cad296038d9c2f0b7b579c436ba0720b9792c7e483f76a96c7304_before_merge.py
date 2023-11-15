    def collect_attributes(self) -> Optional[List[DataclassAttribute]]:
        """Collect all attributes declared in the dataclass and its parents.

        All assignments of the form

          a: SomeType
          b: SomeOtherType = ...

        are collected.
        """
        # First, collect attributes belonging to the current class.
        ctx = self._ctx
        cls = self._ctx.cls
        attrs = []  # type: List[DataclassAttribute]
        known_attrs = set()  # type: Set[str]
        for stmt in cls.defs.body:
            # Any assignment that doesn't use the new type declaration
            # syntax can be ignored out of hand.
            if not (isinstance(stmt, AssignmentStmt) and stmt.new_syntax):
                continue

            # a: int, b: str = 1, 'foo' is not supported syntax so we
            # don't have to worry about it.
            lhs = stmt.lvalues[0]
            if not isinstance(lhs, NameExpr):
                continue

            sym = cls.info.names.get(lhs.name)
            if sym is None:
                # This name is likely blocked by a star import. We don't need to defer because
                # defer() is already called by mark_incomplete().
                continue

            node = sym.node
            if isinstance(node, PlaceholderNode):
                # This node is not ready yet.
                return None
            assert isinstance(node, Var)

            # x: ClassVar[int] is ignored by dataclasses.
            if node.is_classvar:
                continue

            # x: InitVar[int] is turned into x: int and is removed from the class.
            is_init_var = False
            node_type = get_proper_type(node.type)
            if (isinstance(node_type, Instance) and
                    node_type.type.fullname == 'dataclasses.InitVar'):
                is_init_var = True
                node.type = node_type.args[0]

            has_field_call, field_args = _collect_field_args(stmt.rvalue)

            is_in_init_param = field_args.get('init')
            if is_in_init_param is None:
                is_in_init = True
            else:
                is_in_init = bool(ctx.api.parse_bool(is_in_init_param))

            has_default = False
            # Ensure that something like x: int = field() is rejected
            # after an attribute with a default.
            if has_field_call:
                has_default = 'default' in field_args or 'default_factory' in field_args

            # All other assignments are already type checked.
            elif not isinstance(stmt.rvalue, TempNode):
                has_default = True

            if not has_default:
                # Make all non-default attributes implicit because they are de-facto set
                # on self in the generated __init__(), not in the class body.
                sym.implicit = True

            known_attrs.add(lhs.name)
            attrs.append(DataclassAttribute(
                name=lhs.name,
                is_in_init=is_in_init,
                is_init_var=is_init_var,
                has_default=has_default,
                line=stmt.line,
                column=stmt.column,
            ))

        # Next, collect attributes belonging to any class in the MRO
        # as long as those attributes weren't already collected.  This
        # makes it possible to overwrite attributes in subclasses.
        # copy() because we potentially modify all_attrs below and if this code requires debugging
        # we'll have unmodified attrs laying around.
        all_attrs = attrs.copy()
        init_method = cls.info.get_method('__init__')
        for info in cls.info.mro[1:-1]:
            if 'dataclass' not in info.metadata:
                continue

            super_attrs = []
            # Each class depends on the set of attributes in its dataclass ancestors.
            ctx.api.add_plugin_dependency(make_wildcard_trigger(info.fullname))

            for data in info.metadata['dataclass']['attributes']:
                name = data['name']  # type: str
                if name not in known_attrs:
                    attr = DataclassAttribute.deserialize(info, data)
                    if attr.is_init_var and isinstance(init_method, FuncDef):
                        # InitVars are removed from classes so, in order for them to be inherited
                        # properly, we need to re-inject them into subclasses' sym tables here.
                        # To do that, we look 'em up from the parents' __init__.  These variables
                        # are subsequently removed from the sym table at the end of
                        # DataclassTransformer.transform.
                        for arg, arg_name in zip(init_method.arguments, init_method.arg_names):
                            if arg_name == attr.name:
                                cls.info.names[attr.name] = SymbolTableNode(MDEF, arg.variable)

                    known_attrs.add(name)
                    super_attrs.append(attr)
                elif all_attrs:
                    # How early in the attribute list an attribute appears is determined by the
                    # reverse MRO, not simply MRO.
                    # See https://docs.python.org/3/library/dataclasses.html#inheritance for
                    # details.
                    for attr in all_attrs:
                        if attr.name == name:
                            all_attrs.remove(attr)
                            super_attrs.append(attr)
                            break
            all_attrs = super_attrs + all_attrs

        # Ensure that arguments without a default don't follow
        # arguments that have a default.
        found_default = False
        for attr in all_attrs:
            # If we find any attribute that is_in_init but that
            # doesn't have a default after one that does have one,
            # then that's an error.
            if found_default and attr.is_in_init and not attr.has_default:
                # If the issue comes from merging different classes, report it
                # at the class definition point.
                context = (Context(line=attr.line, column=attr.column) if attr in attrs
                           else ctx.cls)
                ctx.api.fail(
                    'Attributes without a default cannot follow attributes with one',
                    context,
                )

            found_default = found_default or (attr.has_default and attr.is_in_init)

        return all_attrs