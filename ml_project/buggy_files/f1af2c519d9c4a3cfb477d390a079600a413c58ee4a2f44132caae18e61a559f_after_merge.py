    def visit_class_def(self, tdef: ClassDef) -> None:
        for type in tdef.info.bases:
            self.analyze(type)
        # Recompute MRO now that we have analyzed all modules, to pick
        # up superclasses of bases imported from other modules in an
        # import loop. (Only do so if we succeeded the first time.)
        if tdef.info.mro:
            tdef.info.mro = []  # Force recomputation
            calculate_class_mro(tdef, self.fail_blocker)
        super().visit_class_def(tdef)