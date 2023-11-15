    def check_method_override(self, defn: Union[FuncDef, OverloadedFuncDef, Decorator]) -> None:
        """Check if function definition is compatible with base classes.

        This may defer the method if a signature is not available in at least one base class.
        """
        # Check against definitions in base classes.
        for base in defn.info.mro[1:]:
            if self.check_method_or_accessor_override_for_base(defn, base):
                # Node was deferred, we will have another attempt later.
                return