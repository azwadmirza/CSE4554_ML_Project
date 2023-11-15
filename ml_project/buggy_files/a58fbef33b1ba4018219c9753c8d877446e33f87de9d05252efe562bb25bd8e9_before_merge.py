    def transform(self) -> None:
        """Apply all the necessary transformations to the underlying
        dataclass so as to ensure it is fully type checked according
        to the rules in PEP 557.
        """
        ctx = self._ctx
        info = self._ctx.cls.info
        attributes = self.collect_attributes()
        if attributes is None:
            # Some definitions are not ready, defer() should be already called.
            return
        for attr in attributes:
            node = info.get(attr.name)
            if node is None:
                # Nodes of superclass InitVars not used in __init__ cannot be reached.
                assert attr.is_init_var and not attr.is_in_init
                continue
            if node.type is None:
                ctx.api.defer()
                return
        decorator_arguments = {
            'init': _get_decorator_bool_argument(self._ctx, 'init', True),
            'eq': _get_decorator_bool_argument(self._ctx, 'eq', True),
            'order': _get_decorator_bool_argument(self._ctx, 'order', False),
            'frozen': _get_decorator_bool_argument(self._ctx, 'frozen', False),
        }

        # If there are no attributes, it may be that the semantic analyzer has not
        # processed them yet. In order to work around this, we can simply skip generating
        # __init__ if there are no attributes, because if the user truly did not define any,
        # then the object default __init__ with an empty signature will be present anyway.
        if (decorator_arguments['init'] and
                ('__init__' not in info.names or info.names['__init__'].plugin_generated) and
                attributes):
            add_method(
                ctx,
                '__init__',
                args=[attr.to_argument(info) for attr in attributes if attr.is_in_init],
                return_type=NoneType(),
            )

        if (decorator_arguments['eq'] and info.get('__eq__') is None or
                decorator_arguments['order']):
            # Type variable for self types in generated methods.
            obj_type = ctx.api.named_type('__builtins__.object')
            self_tvar_expr = TypeVarExpr(SELF_TVAR_NAME, info.fullname + '.' + SELF_TVAR_NAME,
                                         [], obj_type)
            info.names[SELF_TVAR_NAME] = SymbolTableNode(MDEF, self_tvar_expr)

        # Add an eq method, but only if the class doesn't already have one.
        if decorator_arguments['eq'] and info.get('__eq__') is None:
            for method_name in ['__eq__', '__ne__']:
                # The TVar is used to enforce that "other" must have
                # the same type as self (covariant).  Note the
                # "self_type" parameter to add_method.
                obj_type = ctx.api.named_type('__builtins__.object')
                cmp_tvar_def = TypeVarDef(SELF_TVAR_NAME, info.fullname + '.' + SELF_TVAR_NAME,
                                          -1, [], obj_type)
                cmp_other_type = TypeVarType(cmp_tvar_def)
                cmp_return_type = ctx.api.named_type('__builtins__.bool')

                add_method(
                    ctx,
                    method_name,
                    args=[Argument(Var('other', cmp_other_type), cmp_other_type, None, ARG_POS)],
                    return_type=cmp_return_type,
                    self_type=cmp_other_type,
                    tvar_def=cmp_tvar_def,
                )

        # Add <, >, <=, >=, but only if the class has an eq method.
        if decorator_arguments['order']:
            if not decorator_arguments['eq']:
                ctx.api.fail('eq must be True if order is True', ctx.cls)

            for method_name in ['__lt__', '__gt__', '__le__', '__ge__']:
                # Like for __eq__ and __ne__, we want "other" to match
                # the self type.
                obj_type = ctx.api.named_type('__builtins__.object')
                order_tvar_def = TypeVarDef(SELF_TVAR_NAME, info.fullname + '.' + SELF_TVAR_NAME,
                                            -1, [], obj_type)
                order_other_type = TypeVarType(order_tvar_def)
                order_return_type = ctx.api.named_type('__builtins__.bool')
                order_args = [
                    Argument(Var('other', order_other_type), order_other_type, None, ARG_POS)
                ]

                existing_method = info.get(method_name)
                if existing_method is not None and not existing_method.plugin_generated:
                    assert existing_method.node
                    ctx.api.fail(
                        'You may not have a custom %s method when order=True' % method_name,
                        existing_method.node,
                    )

                add_method(
                    ctx,
                    method_name,
                    args=order_args,
                    return_type=order_return_type,
                    self_type=order_other_type,
                    tvar_def=order_tvar_def,
                )

        if decorator_arguments['frozen']:
            self._freeze(attributes)

        self.reset_init_only_vars(info, attributes)

        info.metadata['dataclass'] = {
            'attributes': [attr.serialize() for attr in attributes],
            'frozen': decorator_arguments['frozen'],
        }