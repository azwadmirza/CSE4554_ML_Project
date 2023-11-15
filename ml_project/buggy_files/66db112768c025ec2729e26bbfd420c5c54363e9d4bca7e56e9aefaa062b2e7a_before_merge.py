    def process_soln_file(self,results):

        # the only suffixes that we extract from CPLEX are
        # constraint duals, constraint slacks, and variable
        # reduced-costs. scan through the solver suffix list
        # and throw an exception if the user has specified
        # any others.
        extract_duals = False
        extract_slacks = False
        extract_reduced_costs = False
        extract_rc = False
        extract_lrc = False
        extract_urc = False
        for suffix in self._suffixes:
            flag=False
            if re.match(suffix,"dual"):
                extract_duals = True
                flag=True
            if re.match(suffix,"slack"):
                extract_slacks = True
                flag=True
            if re.match(suffix,"rc"):
                extract_reduced_costs = True
                extract_rc = True
                flag=True
            if re.match(suffix,"lrc"):
                extract_reduced_costs = True
                extract_lrc = True
                flag=True
            if re.match(suffix,"urc"):
                extract_reduced_costs = True
                extract_urc = True
                flag=True
            if not flag:
                raise RuntimeError("***The CPLEX solver plugin cannot extract solution suffix="+suffix)

        # check for existence of the solution file
        # not sure why we just return - would think that we
        # would want to indicate some sort of error
        if not os.path.exists(self._soln_file):
            return

        range_duals = {}
        range_slacks = {}
        soln = Solution()
        soln.objective['__default_objective__'] = {'Value':None}

        # caching for efficiency
        soln_variables = soln.variable
        soln_constraints = soln.constraint

        INPUT = open(self._soln_file, "r")
        results.problem.number_of_objectives=1
        time_limit_exceeded = False
        mip_problem=False
        for line in INPUT:
            line = line.strip()
            line = line.lstrip('<?/')
            line = line.rstrip('/>?')
            tokens=line.split(' ')

            if tokens[0] == "variable":
                variable_name = None
                variable_value = None
                variable_reduced_cost = None
                variable_status = None
                for i in xrange(1,len(tokens)):
                    field_name =  tokens[i].split('=')[0]
                    field_value = tokens[i].split('=')[1].lstrip("\"").rstrip("\"")
                    if field_name == "name":
                        variable_name = field_value
                    elif field_name == "value":
                        variable_value = field_value
                    elif (extract_reduced_costs is True) and (field_name == "reducedCost"):
                        variable_reduced_cost = field_value
                    elif (extract_reduced_costs is True) and (field_name == "status"):
                        variable_status = field_value

                # skip the "constant-one" variable, used to capture/retain objective offsets in the CPLEX LP format.
                if variable_name != "ONE_VAR_CONSTANT":
                    variable = soln_variables[variable_name] = {"Value" : float(variable_value)}
                    if (variable_reduced_cost is not None) and (extract_reduced_costs is True):
                        try:
                            if extract_rc is True:
                                variable["Rc"] = float(variable_reduced_cost)
                            if variable_status is not None:
                                if extract_lrc is True:
                                    if variable_status == "LL":
                                        variable["Lrc"] = float(variable_reduced_cost)
                                    else:
                                        variable["Lrc"] = 0.0
                                if extract_urc is True:
                                    if variable_status == "UL":
                                        variable["Urc"] = float(variable_reduced_cost)
                                    else:
                                        variable["Urc"] = 0.0
                        except:
                            raise ValueError("Unexpected reduced-cost value="+str(variable_reduced_cost)+" encountered for variable="+variable_name)
            elif (tokens[0] == "constraint") and ((extract_duals is True) or (extract_slacks is True)):
                is_range = False
                rlabel = None
                rkey = None
                for i in xrange(1,len(tokens)):
                    field_name =  tokens[i].split('=')[0]
                    field_value = tokens[i].split('=')[1].lstrip("\"").rstrip("\"")
                    if field_name == "name":
                        if field_value.startswith('c_'):
                            constraint = soln_constraints[field_value] = {}
                        elif field_value.startswith('r_l_'):
                            is_range = True
                            rlabel = field_value[4:]
                            rkey = 0
                        elif field_value.startswith('r_u_'):
                            is_range = True
                            rlabel = field_value[4:]
                            rkey = 1
                    elif (extract_duals is True) and (field_name == "dual"): # for LPs
                        if is_range is False:
                            constraint["Dual"] = float(field_value)
                        else:
                            range_duals.setdefault(rlabel,[0,0])[rkey] = float(field_value)
                    elif (extract_slacks is True) and (field_name == "slack"): # for MIPs
                        if is_range is False:
                            constraint["Slack"] = float(field_value)
                        else:
                            range_slacks.setdefault(rlabel,[0,0])[rkey] = float(field_value)
            elif tokens[0].startswith("problemName"):
                filename = (tokens[0].split('=')[1].strip()).lstrip("\"").rstrip("\"")
                results.problem.name = os.path.basename(filename)
                if '.' in results.problem.name:
                    results.problem.name = results.problem.name.split('.')[0]
                tINPUT=open(filename,"r")
                for tline in tINPUT:
                    tline = tline.strip()
                    if tline == "":
                        continue
                    tokens = re.split('[\t ]+',tline)
                    if tokens[0][0] in ['\\', '*']:
                        continue
                    elif tokens[0] == "NAME":
                        results.problem.name = tokens[1]
                    else:
                        sense = tokens[0].lower()
                        if sense in ['max','maximize']:
                            results.problem.sense = ProblemSense.maximize
                        if sense in ['min','minimize']:
                            results.problem.sense = ProblemSense.minimize
                    break
                tINPUT.close()

            elif tokens[0].startswith("objectiveValue"):
                objective_value = (tokens[0].split('=')[1].strip()).lstrip("\"").rstrip("\"")
                soln.objective['__default_objective__']['Value'] = float(objective_value)
            elif tokens[0].startswith("solutionStatusValue"):
               pieces = tokens[0].split("=")
               solution_status = eval(pieces[1])
               # solution status = 1 => optimal
               # solution status = 3 => infeasible
               if soln.status == SolutionStatus.unknown:
                  if solution_status == 1:
                    soln.status = SolutionStatus.optimal
                  elif solution_status == 3:
                    soln.status = SolutionStatus.infeasible
                    soln.gap = None
                  else:
                      # we are flagging anything with a solution status >= 4 as an error, to possibly
                      # be over-ridden as we learn more about the status (e.g., due to time limit exceeded).
                      soln.status = SolutionStatus.error
                      soln.gap = None
            elif tokens[0].startswith("solutionStatusString"):
                solution_status = ((" ".join(tokens).split('=')[1]).strip()).lstrip("\"").rstrip("\"")
                if solution_status in ["optimal", "integer optimal solution", "integer optimal, tolerance"]:
                    soln.status = SolutionStatus.optimal
                    soln.gap = 0.0
                    results.problem.lower_bound = soln.objective['__default_objective__']['Value']
                    results.problem.upper_bound = soln.objective['__default_objective__']['Value']
                    if "integer" in solution_status:
                        mip_problem=True
                elif solution_status in ["infeasible"]:
                    soln.status = SolutionStatus.infeasible
                    soln.gap = None
                elif solution_status in ["time limit exceeded"]:
                    # we need to know if the solution is primal feasible, and if it is, set the solution status accordingly.
                    # for now, just set the flag so we can trigger the logic when we see the primalFeasible keyword.
                    time_limit_exceeded = True
            elif tokens[0].startswith("MIPNodes"):
                if mip_problem:
                    n = eval(eval((" ".join(tokens).split('=')[1]).strip()).lstrip("\"").rstrip("\""))
                    results.solver.statistics.branch_and_bound.number_of_created_subproblems=n
                    results.solver.statistics.branch_and_bound.number_of_bounded_subproblems=n
            elif tokens[0].startswith("primalFeasible") and (time_limit_exceeded is True):
                primal_feasible = int(((" ".join(tokens).split('=')[1]).strip()).lstrip("\"").rstrip("\""))
                if primal_feasible == 1:
                    soln.status = SolutionStatus.feasible
                    if (results.problem.sense == ProblemSense.minimize):
                        results.problem.upper_bound = soln.objective['__default_objective__']['Value']
                    else:
                        results.problem.lower_bound = soln.objective['__default_objective__']['Value']
                else:
                    soln.status = SolutionStatus.infeasible


        if self._best_bound is not None:
            if results.problem.sense == ProblemSense.minimize:
                results.problem.lower_bound = self._best_bound
            else:
                results.problem.upper_bound = self._best_bound
        if self._gap is not None:
            soln.gap = self._gap

        # For the range constraints, supply only the dual with the largest
        # magnitude (at least one should always be numerically zero)
        for key,(ld,ud) in iteritems(range_duals):
            if abs(ld) > abs(ud):
                soln_constraints['r_l_'+key] = {"Dual" : ld}
            else:
                soln_constraints['r_l_'+key] = {"Dual" : ud}                # Use the same key
        # slacks
        for key,(ls,us) in iteritems(range_slacks):
            if abs(ls) > abs(us):
                soln_constraints.setdefault('r_l_'+key,{})["Slack"] = ls
            else:
                soln_constraints.setdefault('r_l_'+key,{})["Slack"] = us    # Use the same key

        if not results.solver.status is SolverStatus.error:
            if results.solver.termination_condition in [TerminationCondition.unknown,
                                                        #TerminationCondition.maxIterations,
                                                        #TerminationCondition.minFunctionValue,
                                                        #TerminationCondition.minStepLength,
                                                        TerminationCondition.globallyOptimal,
                                                        TerminationCondition.locallyOptimal,
                                                        TerminationCondition.optimal,
                                                        #TerminationCondition.maxEvaluations,
                                                        TerminationCondition.other]:
                results.solution.insert(soln)
            elif (results.solver.termination_condition is \
                  TerminationCondition.maxTimeLimit) and \
                  (soln.status is not SolutionStatus.infeasible):
                results.solution.insert(soln)

        INPUT.close()