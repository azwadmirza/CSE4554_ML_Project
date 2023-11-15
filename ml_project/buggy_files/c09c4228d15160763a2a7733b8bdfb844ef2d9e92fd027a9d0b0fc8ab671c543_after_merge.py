    def visit_name(self, node):
        """Check that a name is defined in the current scope"""
        stmt = node.statement()
        if stmt.fromlineno is None:
            # name node from an astroid built from live code, skip
            assert not stmt.root().file.endswith(".py")
            return

        name = node.name
        frame = stmt.scope()
        start_index = len(self._to_consume) - 1

        undefined_variable_is_enabled = self.linter.is_message_enabled(
            "undefined-variable"
        )
        used_before_assignment_is_enabled = self.linter.is_message_enabled(
            "used-before-assignment"
        )

        # iterates through parent scopes, from the inner to the outer
        base_scope_type = self._to_consume[start_index].scope_type
        # pylint: disable=too-many-nested-blocks; refactoring this block is a pain.
        for i in range(start_index, -1, -1):
            current_consumer = self._to_consume[i]

            # The list of base classes in the class definition is not part
            # of the class body.
            # If the current scope is a class scope but it's not the inner
            # scope, ignore it. This prevents to access this scope instead of
            # the globals one in function members when there are some common
            # names.
            if current_consumer.scope_type == "class" and (
                utils.is_ancestor_name(current_consumer.node, node)
                or (i != start_index and self._ignore_class_scope(node))
            ):
                continue

            # if the name node is used as a function default argument's value or as
            # a decorator, then start from the parent frame of the function instead
            # of the function frame - and thus open an inner class scope
            if (
                current_consumer.scope_type == "function"
                and self._defined_in_function_definition(node, current_consumer.node)
            ):
                # ignore function scope if is an annotation/default/decorator, as not in the body
                continue

            if current_consumer.scope_type == "lambda" and utils.is_default_argument(
                node, current_consumer.node
            ):
                continue

            # the name has already been consumed, only check it's not a loop
            # variable used outside the loop
            # avoid the case where there are homonyms inside function scope and
            #  comprehension current scope (avoid bug #1731)
            if name in current_consumer.consumed and not (
                current_consumer.scope_type == "comprehension"
                and self._has_homonym_in_upper_function_scope(node, i)
            ):
                defnode = utils.assign_parent(current_consumer.consumed[name][0])
                self._check_late_binding_closure(node, defnode)
                self._loopvar_name(node, name)
                break

            found_node = current_consumer.get_next_to_consume(node)
            if found_node is None:
                continue

            # checks for use before assignment
            defnode = utils.assign_parent(current_consumer.to_consume[name][0])

            if (
                undefined_variable_is_enabled or used_before_assignment_is_enabled
            ) and defnode is not None:
                self._check_late_binding_closure(node, defnode)
                defstmt = defnode.statement()
                defframe = defstmt.frame()
                # The class reuses itself in the class scope.
                recursive_klass = (
                    frame is defframe
                    and defframe.parent_of(node)
                    and isinstance(defframe, astroid.ClassDef)
                    and node.name == defframe.name
                )

                if (
                    recursive_klass
                    and utils.is_inside_lambda(node)
                    and (
                        not utils.is_default_argument(node)
                        or node.scope().parent.scope() is not defframe
                    )
                ):
                    # Self-referential class references are fine in lambda's --
                    # As long as they are not part of the default argument directly
                    # under the scope of the parent self-referring class.
                    # Example of valid default argument:
                    # class MyName3:
                    #     myattr = 1
                    #     mylambda3 = lambda: lambda a=MyName3: a
                    # Example of invalid default argument:
                    # class MyName4:
                    #     myattr = 1
                    #     mylambda4 = lambda a=MyName4: lambda: a

                    # If the above conditional is True,
                    # there is no possibility of undefined-variable
                    # Also do not consume class name
                    # (since consuming blocks subsequent checks)
                    # -- quit
                    break

                (
                    maybee0601,
                    annotation_return,
                    use_outer_definition,
                ) = self._is_variable_violation(
                    node,
                    name,
                    defnode,
                    stmt,
                    defstmt,
                    frame,
                    defframe,
                    base_scope_type,
                    recursive_klass,
                )

                if use_outer_definition:
                    continue

                if (
                    maybee0601
                    and not utils.is_defined_before(node)
                    and not astroid.are_exclusive(stmt, defstmt, ("NameError",))
                ):

                    # Used and defined in the same place, e.g `x += 1` and `del x`
                    defined_by_stmt = defstmt is stmt and isinstance(
                        node, (astroid.DelName, astroid.AssignName)
                    )
                    if (
                        recursive_klass
                        or defined_by_stmt
                        or annotation_return
                        or isinstance(defstmt, astroid.Delete)
                    ):
                        if not utils.node_ignores_exception(node, NameError):

                            # Handle postponed evaluation of annotations
                            if not (
                                self._postponed_evaluation_enabled
                                and isinstance(
                                    stmt,
                                    (
                                        astroid.AnnAssign,
                                        astroid.FunctionDef,
                                        astroid.Arguments,
                                    ),
                                )
                                and name in node.root().locals
                            ):
                                self.add_message(
                                    "undefined-variable", args=name, node=node
                                )
                    elif base_scope_type != "lambda":
                        # E0601 may *not* occurs in lambda scope.

                        # Handle postponed evaluation of annotations
                        if not (
                            self._postponed_evaluation_enabled
                            and isinstance(
                                stmt, (astroid.AnnAssign, astroid.FunctionDef)
                            )
                        ):
                            self.add_message(
                                "used-before-assignment", args=name, node=node
                            )
                    elif base_scope_type == "lambda":
                        # E0601 can occur in class-level scope in lambdas, as in
                        # the following example:
                        #   class A:
                        #      x = lambda attr: f + attr
                        #      f = 42
                        if isinstance(frame, astroid.ClassDef) and name in frame.locals:
                            if isinstance(node.parent, astroid.Arguments):
                                if stmt.fromlineno <= defstmt.fromlineno:
                                    # Doing the following is fine:
                                    #   class A:
                                    #      x = 42
                                    #      y = lambda attr=x: attr
                                    self.add_message(
                                        "used-before-assignment", args=name, node=node
                                    )
                            else:
                                self.add_message(
                                    "undefined-variable", args=name, node=node
                                )
                        elif current_consumer.scope_type == "lambda":
                            self.add_message("undefined-variable", node=node, args=name)

            current_consumer.mark_as_consumed(name, found_node)
            # check it's not a loop variable used outside the loop
            self._loopvar_name(node, name)
            break
        else:
            # we have not found the name, if it isn't a builtin, that's an
            # undefined name !
            if undefined_variable_is_enabled and not (
                name in astroid.Module.scope_attrs
                or utils.is_builtin(name)
                or name in self.config.additional_builtins
                or (
                    name == "__class__"
                    and isinstance(frame, astroid.FunctionDef)
                    and frame.is_method()
                )
            ):
                if not utils.node_ignores_exception(node, NameError):
                    self.add_message("undefined-variable", args=name, node=node)