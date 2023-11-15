    def visit_class_def(self, tdef: ClassDef) -> None:
        # NamedTuple base classes are validated in check_namedtuple_classdef; we don't have to
        # check them again here.
        if not tdef.info.is_named_tuple:
            for type in tdef.info.bases:
                self.analyze(type)
                if tdef.info.is_protocol:
                    if not isinstance(type, Instance) or not type.type.is_protocol:
                        if type.type.fullname() != 'builtins.object':
                            self.fail('All bases of a protocol must be protocols', tdef)
        # Recompute MRO now that we have analyzed all modules, to pick
        # up superclasses of bases imported from other modules in an
        # import loop. (Only do so if we succeeded the first time.)
        if tdef.info.mro:
            tdef.info.mro = []  # Force recomputation
            calculate_class_mro(tdef, self.fail_blocker)
            if tdef.info.is_protocol:
                add_protocol_members(tdef.info)
        if tdef.analyzed is not None:
            if isinstance(tdef.analyzed, TypedDictExpr):
                self.analyze(tdef.analyzed.info.typeddict_type)
            elif isinstance(tdef.analyzed, NamedTupleExpr):
                self.analyze(tdef.analyzed.info.tuple_type)
        super().visit_class_def(tdef)