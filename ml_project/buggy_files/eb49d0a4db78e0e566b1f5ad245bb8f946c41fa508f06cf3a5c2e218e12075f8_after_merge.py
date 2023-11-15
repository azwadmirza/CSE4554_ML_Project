    def visit_class_def(self, tdef: ClassDef) -> None:
        # NamedTuple base classes are validated in check_namedtuple_classdef; we don't have to
        # check them again here.
        if not tdef.info.is_named_tuple:
            types = list(tdef.info.bases)  # type: List[Type]
            for tvar in tdef.type_vars:
                if tvar.upper_bound:
                    types.append(tvar.upper_bound)
                if tvar.values:
                    types.extend(tvar.values)
            self.analyze_types(types, tdef.info)
            for type in tdef.info.bases:
                if tdef.info.is_protocol:
                    if not isinstance(type, Instance) or not type.type.is_protocol:
                        if type.type.fullname() != 'builtins.object':
                            self.fail('All bases of a protocol must be protocols', tdef)
        # Recompute MRO now that we have analyzed all modules, to pick
        # up superclasses of bases imported from other modules in an
        # import loop. (Only do so if we succeeded the first time.)
        if tdef.info.mro:
            tdef.info.mro = []  # Force recomputation
            mypy.semanal.calculate_class_mro(tdef, self.fail_blocker)
            if tdef.info.is_protocol:
                add_protocol_members(tdef.info)
        if tdef.analyzed is not None:
            # Also check synthetic types associated with this ClassDef.
            # Currently these are TypedDict, and NamedTuple.
            if isinstance(tdef.analyzed, TypedDictExpr):
                self.analyze(tdef.analyzed.info.typeddict_type, tdef.analyzed, warn=True)
            elif isinstance(tdef.analyzed, NamedTupleExpr):
                self.analyze(tdef.analyzed.info.tuple_type, tdef.analyzed, warn=True)
                self.analyze_info(tdef.analyzed.info)
        super().visit_class_def(tdef)