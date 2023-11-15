    def __getattr__(self, name):
        """Retrieve an attribute's value.

        This will compute it if needed, unless it is already on the list of
        attributes being computed.
        """
        if name in self.__pending:
            raise errors.CyclicDefinitionError(
                "Cyclic lazy attribute definition for %r; cycle found in %r." %
                (name, self.__pending))
        elif name in self.__values:
            return self.__values[name]
        elif name in self.__declarations:
            declaration = self.__declarations[name]
            value = declaration.declaration
            if enums.get_builder_phase(value) == enums.BuilderPhase.ATTRIBUTE_RESOLUTION:
                self.__pending.append(name)
                try:
                    value = value.evaluate(
                        instance=self,
                        step=self.__step,
                        extra=declaration.context,
                    )
                finally:
                    last = self.__pending.pop()
                assert name == last

            self.__values[name] = value
            return value
        else:
            raise AttributeError(
                "The parameter %r is unknown. Evaluated attributes are %r, "
                "definitions are %r." % (name, self.__values, self.__declarations))