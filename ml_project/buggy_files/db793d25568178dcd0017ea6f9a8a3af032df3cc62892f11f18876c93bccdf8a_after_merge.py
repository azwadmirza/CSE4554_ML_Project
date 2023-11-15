    def visit_class_def(self, defn: ClassDef) -> Type:
        """Type check a class definition."""
        typ = defn.info
        self.errors.push_type(defn.name)
        self.enter_partial_types()
        old_binder = self.binder
        self.binder = ConditionalTypeBinder()
        with self.binder.top_frame_context():
            self.accept(defn.defs)
        self.binder = old_binder
        if not defn.has_incompatible_baseclass:
            # Otherwise we've already found errors; more errors are not useful
            self.check_multiple_inheritance(typ)
        self.leave_partial_types()
        self.errors.pop_type()