    def _processUnhashableIndex(self, idx):
        """Process a call to __getitem__ with unhashable elements

        There are three basic ways to get here:
          1) the index contains one or more slices or ellipsis
          2) the index contains an unhashable type (e.g., a Pyomo
             (Simple)Component
          3) the index contains an IndexTemplate
        """
        from pyomo.core.expr import current as EXPR
        #
        # Iterate through the index and look for slices and constant
        # components
        #
        fixed = {}
        sliced = {}
        ellipsis = None
        _found_numeric = False
        #
        # Setup the slice template (in fixed)
        #
        if type(idx) is tuple:
            # We would normally do "flatten()" here, but the current
            # (10/2016) implementation of flatten() is too aggressive:
            # it will attempt to expand *any* iterable, including
            # SimpleParam.
            idx = pyutilib.misc.flatten_tuple(idx)
        elif type(idx) is list:
            idx = pyutilib.misc.flatten_tuple(tuple(idx))
        else:
            idx = (idx,)

        for i,val in enumerate(idx):
            if type(val) is slice:
                if val.start is not None or val.stop is not None:
                    raise IndexError(
                        "Indexed components can only be indexed with simple "
                        "slices: start and stop values are not allowed.")
                if val.step is not None:
                    logger.warning(
                        "DEPRECATION WARNING: The special wildcard slice "
                        "(::0) is deprecated.  Please use an ellipsis (...) "
                        "to indicate '0 or more' indices")
                    val = Ellipsis
                else:
                    if ellipsis is None:
                        sliced[i] = val
                    else:
                        sliced[i-len(idx)] = val
                    continue

            if val is Ellipsis:
                if ellipsis is not None:
                    raise IndexError(
                        "Indexed components can only be indexed with simple "
                        "slices: the Pyomo wildcard slice (Ellipsis; "
                        "e.g., '...') can only appear once")
                ellipsis = i
                continue

            if hasattr(val, 'is_expression_type'):
                _num_val = val
                # Attempt to retrieve the numeric value .. if this
                # is a template expression generation, then it
                # should raise a TemplateExpressionError
                try:
                    val = EXPR.evaluate_expression(val, constant=True)
                    _found_numeric = True

                except TemplateExpressionError:
                    #
                    # The index is a template expression, so return the
                    # templatized expression.
                    #
                    from pyomo.core.expr import current as EXPR
                    return EXPR.GetItemExpression(tuple(idx), self)

                except EXPR.NonConstantExpressionError:
                    #
                    # The expression contains an unfixed variable
                    #
                    raise RuntimeError(
"""Error retrieving the value of an indexed item %s:
index %s is not a constant value.  This is likely not what you meant to
do, as if you later change the fixed value of the object this lookup
will not change.  If you understand the implications of using
non-constant values, you can get the current value of the object using
the value() function.""" % ( self.name, i ))

                except EXPR.FixedExpressionError:
                    #
                    # The expression contains a fixed variable
                    #
                    raise RuntimeError(
"""Error retrieving the value of an indexed item %s:
index %s is a fixed but not constant value.  This is likely not what you
meant to do, as if you later change the fixed value of the object this
lookup will not change.  If you understand the implications of using
fixed but not constant values, you can get the current value using the
value() function.""" % ( self.name, i ))
                #
                # There are other ways we could get an exception such as
                # evaluating a Param / Var that is not initialized.
                # These exceptions will continue up the call stack.
                #

            # verify that the value is hashable
            hash(val)
            if ellipsis is None:
                fixed[i] = val
            else:
                fixed[i - len(idx)] = val

        if sliced or ellipsis is not None:
            return _IndexedComponent_slice(self, fixed, sliced, ellipsis)
        elif _found_numeric:
            if len(idx) == 1:
                return fixed[0]
            else:
                return tuple( fixed[i] for i in range(len(idx)) )
        else:
            raise DeveloperError(
                "Unknown problem encountered when trying to retrieve "
                "index for component %s" % (self.name,) )