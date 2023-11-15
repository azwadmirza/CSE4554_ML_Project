    def _add_numeric_methods_unary(cls):
        """
        Add in numeric unary methods.
        """
        def _make_evaluate_unary(op, opstr):

            def _evaluate_numeric_unary(self):

                self._validate_for_numeric_unaryop(op, opstr)
                attrs = self._get_attributes_dict()
                attrs = self._maybe_update_attributes(attrs)
                return Index(op(self.values), **attrs)

            _evaluate_numeric_unary.__name__ = opstr
            return _evaluate_numeric_unary

        cls.__neg__ = _make_evaluate_unary(operator.neg, '__neg__')
        cls.__pos__ = _make_evaluate_unary(operator.pos, '__pos__')
        cls.__abs__ = _make_evaluate_unary(np.abs, '__abs__')
        cls.__inv__ = _make_evaluate_unary(lambda x: -x, '__inv__')