        def _make_evaluate_unary(op, opstr):

            def _evaluate_numeric_unary(self):

                self._validate_for_numeric_unaryop(op, opstr)
                attrs = self._get_attributes_dict()
                attrs = self._maybe_update_attributes(attrs)
                return Index(op(self.values), **attrs)

            _evaluate_numeric_unary.__name__ = opstr
            return _evaluate_numeric_unary