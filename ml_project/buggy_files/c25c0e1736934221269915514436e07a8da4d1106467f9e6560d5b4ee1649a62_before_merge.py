    def check_generator_or_comprehension(self, gen: GeneratorExpr,
                                         type_name: str,
                                         id_for_messages: str) -> Type:
        """Type check a generator expression or a list comprehension."""
        with self.chk.binder.frame_context():
            self.check_for_comp(gen)

            # Infer the type of the list comprehension by using a synthetic generic
            # callable type.
            tvdef = TypeVarDef('T', -1, [], self.chk.object_type())
            tv = TypeVarType(tvdef)
            constructor = CallableType(
                [tv],
                [nodes.ARG_POS],
                [None],
                self.chk.named_generic_type(type_name, [tv]),
                self.chk.named_type('builtins.function'),
                name=id_for_messages,
                variables=[tvdef])
            return self.check_call(constructor,
                                [gen.left_expr], [nodes.ARG_POS], gen)[0]