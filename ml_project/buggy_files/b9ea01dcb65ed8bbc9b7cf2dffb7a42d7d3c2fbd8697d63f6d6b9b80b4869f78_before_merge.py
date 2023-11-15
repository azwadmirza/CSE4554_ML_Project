    def _Q_opt(self, ThetaVals=None, solver="ef_ipopt",
               return_values=[], bootlist=None, calc_cov=False):
        """
        Set up all thetas as first stage Vars, return resulting theta
        values as well as the objective function value.

        NOTE: If thetavals is present it will be attached to the
        scenario tree so it can be used by the scenario creation
        callback.  Side note (feb 2018, dlw): if you later decide to
        construct the tree just once and reuse it, then remember to
        remove thetavals from it when none is desired.
        """
        
        assert(solver != "k_aug" or ThetaVals == None)
        # Create a tree with dummy scenarios (callback will supply when needed).
        # Which names to use (i.e., numbers) depends on if it is for bootstrap.
        # (Bootstrap scenarios will use indirection through the bootlist)
        if bootlist is None:
            tree_model = _treemaker(self._numbers_list)
        else:
            tree_model = _treemaker(range(len(self._numbers_list)))
        stage1 = tree_model.Stages[1]
        stage2 = tree_model.Stages[2]
        tree_model.StageVariables[stage1] = self.theta_names
        tree_model.StageVariables[stage2] = []
        tree_model.StageCost[stage1] = "FirstStageCost"
        tree_model.StageCost[stage2] = "SecondStageCost"

        # Now attach things to the tree_model to pass them to the callback
        tree_model.CallbackModule = None
        tree_model.CallbackFunction = self._instance_creation_callback
        if ThetaVals is not None:
            tree_model.ThetaVals = ThetaVals
        if bootlist is not None:
            tree_model.BootList = bootlist
        tree_model.cb_data = self.callback_data  # None is OK

        stsolver = st.StochSolver(fsfile = "pyomo.contrib.parmest.parmest",
                                  fsfct = "_pysp_instance_creation_callback",
                                  tree_model = tree_model)
                
        # Solve the extensive form with ipopt
        if solver == "ef_ipopt":
        
            # Generate the extensive form of the stochastic program using pysp
            self.ef_instance = stsolver.make_ef()

            # need_gap is a holdover from solve_ef in rapper.py. Would we ever want
            # need_gap = True with parmest?
            need_gap = False
            
            assert not (need_gap and self.calc_cov), "Calculating both the gap and reduced hessian (covariance) is not currently supported."

            if not calc_cov:
                # Do not calculate the reduced hessian

                solver = SolverFactory('ipopt')
                if self.solver_options is not None:
                    for key in self.solver_options:
                        solver.options[key] = self.solver_options[key]

                if need_gap:
                    solve_result = solver.solve(self.ef_instance, tee = self.tee, load_solutions=False)
                    if len(solve_result.solution) > 0:
                        absgap = solve_result.solution(0).gap
                    else:
                        absgap = None
                    self.ef_instance.solutions.load_from(solve_result)
                else:
                    solve_result = solver.solve(self.ef_instance, tee = self.tee)

            elif not asl_available:
                raise ImportError("parmest requires ASL to calculate the covariance matrix with solver 'ipopt'")
            else:
                # parmest makes the fitted parameters stage 1 variables
                # thus we need to convert from var names (string) to 
                # Pyomo vars
                ind_vars = []
                for v in self.theta_names:

                    #ind_vars.append(eval('ef.'+v))
                    ind_vars.append(self.ef_instance.MASTER_BLEND_VAR_RootNode[v])
        
                # calculate the reduced hessian
                solve_result, inv_red_hes = inv_reduced_hessian_barrier(self.ef_instance, 
                    independent_variables= ind_vars,
                    solver_options=self.solver_options,
                    tee=self.tee)
            
            # Extract solution from pysp
            stsolver.scenario_tree.pullScenarioSolutionsFromInstances()
            stsolver.scenario_tree.snapshotSolutionFromScenarios() # update nodes
                                
            if self.diagnostic_mode:
                print('    Solver termination condition = ',
                       str(solve_result.solver.termination_condition))

            # assume all first stage are thetas...
            thetavals = {}
            for name, solval in stsolver.root_Var_solution():
                 thetavals[name] = solval

            objval = stsolver.root_E_obj()
            
            if calc_cov:
                # Calculate the covariance matrix
                
                # Extract number of data points considered
                n = len(self.callback_data)
                
                # Extract number of fitted parameters
                l = len(thetavals)
                
                # Assumption: Objective value is sum of squared errors
                sse = objval
                
                '''Calculate covariance assuming experimental observation errors are
                independent and follow a Gaussian 
                distribution with constant variance.
                
                The formula used in parmest was verified against equations (7-5-15) and
                (7-5-16) in "Nonlinear Parameter Estimation", Y. Bard, 1974.
                
                This formula is also applicable if the objective is scaled by a constant;
                the constant cancels out. (PySP scaled by 1/n because it computes an
                expected value.)
                '''
                cov = 2 * sse / (n - l) * inv_red_hes
            
            if len(return_values) > 0:
                var_values = []
                for exp_i in stsolver.ef_instance.component_objects(Block, descend_into=False):
                    vals = {}
                    for var in return_values:
                        exp_i_var = eval('exp_i.'+ str(var))
                        temp = [_.value for _ in exp_i_var.itervalues()]
                        if len(temp) == 1:
                            vals[var] = temp[0]
                        else:
                            vals[var] = temp                    
                    var_values.append(vals)                    
                var_values = pd.DataFrame(var_values)
                if calc_cov:
                    return objval, thetavals, var_values, cov
                else:
                    return objval, thetavals, var_values

            if calc_cov:
                return objval, thetavals, cov
            else:
                return objval, thetavals
        
        # Solve with sipopt and k_aug
        elif solver == "k_aug":
            # Just hope for the best with respect to degrees of freedom.

            model = stsolver.make_ef()
            stream_solver = True
            ipopt = SolverFactory('ipopt')
            sipopt = SolverFactory('ipopt_sens')
            kaug = SolverFactory('k_aug')

            #: ipopt suffixes  REQUIRED FOR K_AUG!
            model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT_EXPORT)
            model.ipopt_zL_out = pyo.Suffix(direction=pyo.Suffix.IMPORT)
            model.ipopt_zU_out = pyo.Suffix(direction=pyo.Suffix.IMPORT)
            model.ipopt_zL_in = pyo.Suffix(direction=pyo.Suffix.EXPORT)
            model.ipopt_zU_in = pyo.Suffix(direction=pyo.Suffix.EXPORT)

            # declare the suffix to be imported by the solver
            model.red_hessian = pyo.Suffix(direction=pyo.Suffix.EXPORT)
            #: K_AUG SUFFIXES
            model.dof_v = pyo.Suffix(direction=pyo.Suffix.EXPORT) 
            model.rh_name = pyo.Suffix(direction=pyo.Suffix.IMPORT)

            for vstrindex in range(len(self.theta_names)):
                vstr = self.theta_names[vstrindex]
                varobject = _ef_ROOT_node_Object_from_string(model, vstr)
                varobject.set_suffix_value(model.red_hessian, vstrindex+1)
                varobject.set_suffix_value(model.dof_v, 1)
            
            #: rh_name will tell us which position the corresponding variable has on the reduced hessian text file.
            #: be sure to declare the suffix value (order)
            # dof_v is "degree of freedom variable"
            kaug.options["compute_inv"] = ""  #: if the reduced hessian is desired.
            #: please check the inv_.in file if the compute_inv option was used

            #: write some options for ipopt sens
            with open('ipopt.opt', 'w') as f:
                f.write('compute_red_hessian yes\n')  #: computes the reduced hessian (sens_ipopt)
                f.write('output_file my_ouput.txt\n')
                f.write('rh_eigendecomp yes\n')
                f.close()
            #: Solve
            sipopt.solve(model, tee=stream_solver)
            with open('ipopt.opt', 'w') as f:
                f.close()

            ipopt.solve(model, tee=stream_solver)

            model.ipopt_zL_in.update(model.ipopt_zL_out)
            model.ipopt_zU_in.update(model.ipopt_zU_out)

            #: k_aug
            print('k_aug \n\n\n')
            #m.write('problem.nl', format=ProblemFormat.nl)
            kaug.solve(model, tee=stream_solver)
            HessDict = {}
            thetavals = {}
            print('k_aug red_hess')
            with open('result_red_hess.txt', 'r') as f:
                lines = f.readlines()
            # asseble the return values
            objval = model.MASTER_OBJECTIVE_EXPRESSION.expr()
            for i in range(len(lines)):
                HessDict[self.theta_names[i]] = {}
                linein = lines[i]
                print(linein)
                parts = linein.split()
                for j in range(len(parts)):
                    HessDict[self.theta_names[i]][self.theta_names[j]] = \
                        float(parts[j])
                # Get theta value (there is probably a better way...)
                vstr = self.theta_names[i]
                varobject = _ef_ROOT_node_Object_from_string(model, vstr)
                thetavals[self.theta_names[i]] = pyo.value(varobject)
            return objval, thetavals, HessDict

        else:
            raise RuntimeError("Unknown solver in Q_Opt="+solver)