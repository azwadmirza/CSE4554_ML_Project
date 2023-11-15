    def __init__(self, m, package='scipy'):
        
        self._intpackage = package
        if self._intpackage not in ['scipy', 'casadi']:
            raise DAE_Error(
                "Unrecognized simulator package %s. Please select from "
                "%s" % (self._intpackage, ['scipy', 'casadi']))

        if self._intpackage == 'scipy':
            if not scipy_available:
                # Converting this to a warning so that Simulator initialization
                # can be tested even when scipy is unavailable
                logger.warning("The scipy module is not available. You may "
                               "build the Simulator object but you will not "
                               "be able to run the simulation.")
        else:
            if not casadi_available:
                # Initializing the simulator for use with casadi requires
                # access to casadi objects. Therefore, we must throw an error
                # here instead of a warning. 
                raise ValueError("The casadi module is not available. "
                                  "Cannot simulate model.")

        # Check for active Blocks and throw error if any are found
        if len(list(m.component_data_objects(Block, active=True,
                                             descend_into=False))):
            raise DAE_Error("The Simulator cannot handle hierarchical models "
                            "at the moment.")

        temp = m.component_map(ContinuousSet)
        if len(temp) != 1:
            raise DAE_Error(
                "Currently the simulator may only be applied to "
                "Pyomo models with a single ContinuousSet")

        # Get the ContinuousSet in the model
        contset = list(temp.values())[0]

        # Create a index template for the continuous set
        cstemplate = IndexTemplate(contset)

        # Ensure that there is at least one derivative in the model
        derivs = m.component_map(DerivativeVar)
        if len(derivs) == 0:
            raise DAE_Error("Cannot simulate a model with no derivatives")

        templatemap = {}  # Map for template substituter
        rhsdict = {}  # Map of derivative to its RHS templated expr
        derivlist = []  # Ordered list of derivatives
        alglist = []  # list of templated algebraic equations

        # Loop over constraints to find differential equations with separable
        # RHS. Must find a RHS for every derivative var otherwise ERROR. Build
        # dictionary of DerivativeVar:RHS equation.
        for con in m.component_objects(Constraint, active=True):
            
            # Skip the discretization equations if model is discretized
            if '_disc_eq' in con.name:
                continue
            
            # Check dimension of the Constraint. Check if the
            # Constraint is indexed by the continuous set and
            # determine its order in the indexing sets
            if con.dim() == 0:
                continue
            elif con._implicit_subsets is None:
                # Check if the continuous set is the indexing set
                if con._index is not contset:
                    continue
                else:
                    csidx = 0
                    noncsidx = (None,)
            else:
                temp = con._implicit_subsets
                dimsum = 0
                csidx = -1
                noncsidx = None
                for s in temp:
                    if s is contset:
                        if csidx != -1:
                            raise DAE_Error(
                                "Cannot simulate the constraint %s because "
                                "it is indexed by duplicate ContinuousSets"
                                % con.name)
                        csidx = dimsum
                    elif noncsidx is None:
                        noncsidx = s
                    else:
                        noncsidx = noncsidx.cross(s)
                    dimsum += s.dimen
                if csidx == -1:
                    continue

            # Get the rule used to construct the constraint
            conrule = con.rule

            for i in noncsidx:
                # Insert the index template and call the rule to
                # create a templated expression              
                if i is None:
                    tempexp = conrule(m, cstemplate)
                else:
                    if not isinstance(i, tuple):
                        i = (i,)
                    tempidx = i[0:csidx] + (cstemplate,) + i[csidx:]
                    tempexp = conrule(m, *tempidx)

                # Check to make sure it's an EqualityExpression
                if not type(tempexp) is EXPR.EqualityExpression:
                    continue
            
                # Check to make sure it's a differential equation with
                # separable RHS
                args = None
                # Case 1: m.dxdt[t] = RHS 
                if type(tempexp.arg(0)) is EXPR.GetItemExpression:
                    args = _check_getitemexpression(tempexp, 0)
            
                # Case 2: RHS = m.dxdt[t]
                if args is None:
                    if type(tempexp.arg(1)) is EXPR.GetItemExpression:
                        args = _check_getitemexpression(tempexp, 1)

                # Case 3: m.p*m.dxdt[t] = RHS
                if args is None:
                    if type(tempexp.arg(0)) is EXPR.ProductExpression or \
                       type(tempexp.arg(0)) is EXPR.ReciprocalExpression:
                        args = _check_productexpression(tempexp, 0)

                # Case 4: RHS =  m.p*m.dxdt[t]
                if args is None:
                    if type(tempexp.arg(1)) is EXPR.ProductExpression or \
                       type(tempexp.arg(1)) is EXPR.ReciprocalExpression:
                        args = _check_productexpression(tempexp, 1)

                # Case 5: m.dxdt[t] + sum(ELSE) = RHS
                # or CONSTANT + m.dxdt[t] = RHS
                if args is None:
                    if type(tempexp.arg(0)) is EXPR.SumExpression:
                        args = _check_viewsumexpression(tempexp, 0)

                # Case 6: RHS = m.dxdt[t] + sum(ELSE)
                if args is None:
                    if type(tempexp.arg(1)) is EXPR.SumExpression:
                        args = _check_viewsumexpression(tempexp, 1)

                # Case 7: RHS = m.p*m.dxdt[t] + CONSTANT
                # This case will be caught by Case 6 if p is immutable. If
                # p is mutable then this case will not be detected as a
                # separable differential equation

                # Case 8: - dxdt[t] = RHS
                if args is None:
                    if type(tempexp.arg(0)) is EXPR.NegationExpression:
                        args = _check_negationexpression(tempexp, 0)

                # Case 9: RHS = - dxdt[t]
                if args is None:
                    if type(tempexp.arg(1)) is EXPR.NegationExpression:
                        args = _check_negationexpression(tempexp, 1)


                # At this point if args is not None then args[0] contains
                # the _GetItemExpression for the DerivativeVar and args[1]
                # contains the RHS expression. If args is None then the
                # constraint is considered an algebraic equation
                if args is None:
                    # Constraint is an algebraic equation or unsupported
                    # differential equation
                    if self._intpackage == 'scipy':
                        raise DAE_Error(
                            "Model contains an algebraic equation or "
                            "unrecognized differential equation. Constraint "
                            "'%s' cannot be simulated using Scipy. If you are "
                            "trying to simulate a DAE model you must use "
                            "CasADi as the integration package."
                            % str(con.name))
                    tempexp = tempexp.arg(0) - tempexp.arg(1)
                    algexp = substitute_pyomo2casadi(tempexp, templatemap)
                    alglist.append(algexp)
                    continue
            
                # Add the differential equation to rhsdict and derivlist
                dv = args[0]
                RHS = args[1]
                dvkey = _GetItemIndexer(dv)
                if dvkey in rhsdict.keys():
                    raise DAE_Error(
                        "Found multiple RHS expressions for the "
                        "DerivativeVar %s" % str(dvkey))
            
                derivlist.append(dvkey)
                if self._intpackage is 'casadi':
                    rhsdict[dvkey] = substitute_pyomo2casadi(RHS, templatemap)
                else:
                    rhsdict[dvkey] = convert_pyomo2scipy(RHS, templatemap)
        # Check to see if we found a RHS for every DerivativeVar in
        # the model
        # FIXME: Not sure how to rework this for multi-index case
        # allderivs = derivs.keys()
        # if set(allderivs) != set(derivlist):
        #     missing = list(set(allderivs)-set(derivlist))
        #     print("WARNING: Could not find a RHS expression for the "
        #     "following DerivativeVar components "+str(missing))

        # Create ordered list of differential variables corresponding
        # to the list of derivatives.
        diffvars = []

        for deriv in derivlist:
            sv = deriv._base.get_state_var()
            diffvars.append(_GetItemIndexer(sv[deriv._args]))

        # Create ordered list of algebraic variables and time-varying
        # parameters
        algvars = []

        for item in iterkeys(templatemap):
            if item._base.name in derivs.keys():
                # Make sure there are no DerivativeVars in the
                # template map
                raise DAE_Error(
                    "Cannot simulate a differential equation with "
                    "multiple DerivativeVars")
            if item not in diffvars:
                # Finds time varying parameters and algebraic vars
                algvars.append(item)
                
        if self._intpackage == 'scipy':
            # Function sent to scipy integrator
            def _rhsfun(t, x):
                residual = []
                cstemplate.set_value(t)
                for idx, v in enumerate(diffvars):
                    if v in templatemap:
                        templatemap[v].set_value(x[idx])

                for d in derivlist:
                    residual.append(rhsdict[d]())

                return residual
            self._rhsfun = _rhsfun   
            
        # Add any diffvars not added by expression walker to self._templatemap
        if self._intpackage == 'casadi':
            for _id in diffvars:
                if _id not in templatemap:
                    name = "%s[%s]" % (
                        _id._base.name, ','.join(str(x) for x in _id._args))
                    templatemap[_id] = casadi.SX.sym(name)

        self._contset = contset
        self._cstemplate = cstemplate
        self._diffvars = diffvars
        self._derivlist = derivlist
        self._templatemap = templatemap
        self._rhsdict = rhsdict
        self._alglist = alglist
        self._algvars = algvars
        self._model = m
        self._tsim = None
        self._simsolution = None
        # The algebraic vars in the most recent simulation
        self._simalgvars = None
        # The time-varying inputs in the most recent simulation
        self._siminputvars = None