    def calculate_class_mro(self, defn: ClassDef,
                            obj_type: Optional[Callable[[], Instance]] = None) -> None:
        """Calculate method resolution order for a class.

        `obj_type` may be omitted in the third pass when all classes are already analyzed.
        It exists just to fill in empty base class list during second pass in case of
        an import cycle.
        """
        try:
            calculate_mro(defn.info, obj_type)
        except MroError:
            self.fail_blocker('Cannot determine consistent method resolution '
                              'order (MRO) for "%s"' % defn.name, defn)
            defn.info.mro = []
        # Allow plugins to alter the MRO to handle the fact that `def mro()`
        # on metaclasses permits MRO rewriting.
        if defn.fullname:
            hook = self.plugin.get_customize_class_mro_hook(defn.fullname)
            if hook:
                hook(ClassDefContext(defn, FakeExpression(), self))