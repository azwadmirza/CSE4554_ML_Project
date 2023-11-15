    def analyze_base_classes(self, defn: ClassDef) -> None:
        """Analyze and set up base classes.

        This computes several attributes on the corresponding TypeInfo defn.info
        related to the base classes: defn.info.bases, defn.info.mro, and
        miscellaneous others (at least tuple_type, fallback_to_any, and is_enum.)
        """

        base_types = []  # type: List[Instance]
        info = defn.info

        for base_expr in defn.base_type_exprs:
            try:
                base = self.expr_to_analyzed_type(base_expr)
            except TypeTranslationError:
                self.fail('Invalid base class', base_expr)
                info.fallback_to_any = True
                continue

            if isinstance(base, TupleType):
                if info.tuple_type:
                    self.fail("Class has two incompatible bases derived from tuple", defn)
                    defn.has_incompatible_baseclass = True
                info.tuple_type = base
                base_types.append(base.fallback)
            elif isinstance(base, Instance):
                if base.type.is_newtype:
                    self.fail("Cannot subclass NewType", defn)
                base_types.append(base)
            elif isinstance(base, AnyType):
                if self.options.disallow_subclassing_any:
                    if isinstance(base_expr, (NameExpr, MemberExpr)):
                        msg = "Class cannot subclass '{}' (has type 'Any')".format(base_expr.name)
                    else:
                        msg = "Class cannot subclass value of type 'Any'"
                    self.fail(msg, base_expr)
                info.fallback_to_any = True
            else:
                self.fail('Invalid base class', base_expr)
                info.fallback_to_any = True
            if 'unimported' in self.options.disallow_any and has_any_from_unimported_type(base):
                if isinstance(base_expr, (NameExpr, MemberExpr)):
                    prefix = "Base type {}".format(base_expr.name)
                else:
                    prefix = "Base type"
                self.msg.unimported_type_becomes_any(prefix, base, base_expr)
            check_for_explicit_any(base, self.options, self.is_typeshed_stub_file, self.msg,
                                   context=base_expr)

        # Add 'object' as implicit base if there is no other base class.
        if (not base_types and defn.fullname != 'builtins.object'):
            base_types.append(self.object_type())

        info.bases = base_types

        # Calculate the MRO. It might be incomplete at this point if
        # the bases of defn include classes imported from other
        # modules in an import loop. We'll recompute it in ThirdPass.
        if not self.verify_base_classes(defn):
            # Give it an MRO consisting of just the class itself and object.
            defn.info.mro = [defn.info, self.object_type().type]
            return
        calculate_class_mro(defn, self.fail_blocker)
        # If there are cyclic imports, we may be missing 'object' in
        # the MRO. Fix MRO if needed.
        if info.mro and info.mro[-1].fullname() != 'builtins.object':
            info.mro.append(self.object_type().type)
        if defn.info.is_enum and defn.type_vars:
            self.fail("Enum class cannot be generic", defn)