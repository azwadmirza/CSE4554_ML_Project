    def analyze_base_classes(self, defn: ClassDef) -> None:
        """Analyze and set up base classes.

        This computes several attributes on the corresponding TypeInfo defn.info
        related to the base classes: defn.info.bases, defn.info.mro, and
        miscellaneous others (at least tuple_type, fallback_to_any, and is_enum.)
        """

        base_types = []  # type: List[Instance]
        for base_expr in defn.base_type_exprs:
            try:
                base = self.expr_to_analyzed_type(base_expr)
            except TypeTranslationError:
                self.fail('Invalid base class', base_expr)
                defn.info.fallback_to_any = True
                continue

            if isinstance(base, TupleType):
                if defn.info.tuple_type:
                    self.fail("Class has two incompatible bases derived from tuple", defn)
                if (not self.is_stub_file
                        and not defn.info.is_named_tuple
                        and base.fallback.type.fullname() == 'builtins.tuple'):
                    self.fail("Tuple[...] not supported as a base class outside a stub file", defn)
                defn.info.tuple_type = base
                base_types.append(base.fallback)
            elif isinstance(base, Instance):
                base_types.append(base)
            elif isinstance(base, AnyType):
                defn.info.fallback_to_any = True
            else:
                self.fail('Invalid base class', base_expr)
                defn.info.fallback_to_any = True

        # Add 'object' as implicit base if there is no other base class.
        if (not base_types and defn.fullname != 'builtins.object'):
            base_types.append(self.object_type())

        defn.info.bases = base_types

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
        if defn.info.mro and defn.info.mro[-1].fullname() != 'builtins.object':
            defn.info.mro.append(self.object_type().type)