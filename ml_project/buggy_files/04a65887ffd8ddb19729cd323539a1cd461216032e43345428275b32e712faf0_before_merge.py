    def __call__(self, eqs, variables=None, method_options=None):
        '''
        Apply a state updater description to model equations.
        
        Parameters
        ----------
        eqs : `Equations`
            The equations describing the model
        variables: dict-like, optional
            The `Variable` objects for the model. Ignored by the explicit
            state updater.
        method_options : dict, optional
            Additional options to the state updater (not used at the moment
            for the explicit state updaters).

        Examples
        --------
        >>> from brian2 import *
        >>> eqs = Equations('dv/dt = -v / tau : volt')
        >>> print(euler(eqs))
        _v = -dt*v/tau + v
        v = _v
        >>> print(rk4(eqs))
        __k_1_v = -dt*v/tau
        __k_2_v = -dt*(0.5*__k_1_v + v)/tau
        __k_3_v = -dt*(0.5*__k_2_v + v)/tau
        __k_4_v = -dt*(__k_3_v + v)/tau
        _v = 0.166666666666667*__k_1_v + 0.333333333333333*__k_2_v + 0.333333333333333*__k_3_v + 0.166666666666667*__k_4_v + v
        v = _v
        '''
        method_options = extract_method_options(method_options, {})
        # Non-stochastic numerical integrators should work for all equations,
        # except for stochastic equations
        if eqs.is_stochastic and self.stochastic is None:
            raise UnsupportedEquationsException('Cannot integrate '
                                                'stochastic equations with '
                                                'this state updater.')
        if self.custom_check:
            self.custom_check(eqs, variables)
        # The final list of statements
        statements = []

        stochastic_variables = eqs.stochastic_variables

        # The variables for the intermediate results in the state updater
        # description, e.g. the variable k in rk2
        intermediate_vars = [var for var, expr in self.statements]
        
        # A dictionary mapping all the variables in the equations to their
        # sympy representations 
        eq_variables = dict(((var, _symbol(var)) for var in eqs.eq_names))
        
        # Generate the random numbers for the stochastic variables
        for stochastic_variable in stochastic_variables:
            statements.append(stochastic_variable + ' = ' + 'dt**.5 * randn()')

        substituted_expressions = eqs.get_substituted_expressions(variables)

        # Process the intermediate statements in the stateupdater description
        for intermediate_var, intermediate_expr in self.statements:
                      
            # Split the expression into a non-stochastic and a stochastic part
            non_stochastic_expr, stochastic_expr = split_expression(intermediate_expr)
            
            # Execute the statement by appropriately replacing the functions f
            # and g and the variable x for every equation in the model.
            # We use the model equations where the subexpressions have
            # already been substituted into the model equations.
            for var, expr in substituted_expressions:
                for xi in stochastic_variables:
                    RHS = self._generate_RHS(eqs, var, eq_variables, intermediate_vars,
                                             expr, non_stochastic_expr,
                                             stochastic_expr, xi)
                    statements.append(intermediate_var+'_'+var+'_'+xi+' = '+RHS)
                if not stochastic_variables:   # no stochastic variables
                    RHS = self._generate_RHS(eqs, var, eq_variables, intermediate_vars,
                                             expr, non_stochastic_expr,
                                             stochastic_expr)
                    statements.append(intermediate_var+'_'+var+' = '+RHS)
                
        # Process the "return" line of the stateupdater description
        non_stochastic_expr, stochastic_expr = split_expression(self.output)

        if eqs.is_stochastic and (self.stochastic != 'multiplicative' and
                                  eqs.stochastic_type == 'multiplicative'):
            # The equations are marked as having multiplicative noise and the
            # current state updater does not support such equations. However,
            # it is possible that the equations do not use multiplicative noise
            # at all. They could depend on time via a function that is constant
            # over a single time step (most likely, a TimedArray). In that case
            # we can integrate the equations
            dt_value = variables['dt'].get_value()[0] if 'dt' in variables else None
            for _, expr in substituted_expressions:
                _, stoch = expr.split_stochastic()
                if stoch is None:
                    continue
                # There could be more than one stochastic variable (e.g. xi_1, xi_2)
                for _, stoch_expr in stoch.items():
                    sympy_expr = str_to_sympy(stoch_expr.code)
                    # The equation really has multiplicative noise, if it depends
                    # on time (and not only via a function that is constant
                    # over dt), or if it depends on another variable defined
                    # via differential equations.
                    if (not is_constant_over_dt(sympy_expr, variables, dt_value)
                            or len(stoch_expr.identifiers & eqs.diff_eq_names)):
                        raise UnsupportedEquationsException('Cannot integrate '
                                                            'equations with '
                                                            'multiplicative noise with '
                                                            'this state updater.')

        # Assign a value to all the model variables described by differential
        # equations
        for var, expr in substituted_expressions:
            RHS = self._generate_RHS(eqs, var, eq_variables, intermediate_vars,
                                     expr, non_stochastic_expr, stochastic_expr,
                                     stochastic_variables)
            statements.append('_' + var + ' = ' + RHS)
        
        # Assign everything to the final variables
        for var, expr in substituted_expressions:
            statements.append(var + ' = ' + '_' + var)

        return '\n'.join(statements)