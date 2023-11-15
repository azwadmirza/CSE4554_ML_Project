    def _transformBlock(self, block, currentds):

        self._fe = {}
        for ds in block.component_objects(ContinuousSet):
            if currentds is None or currentds == ds.name or currentds is ds:
                generate_finite_elements(ds, self._nfe[currentds])
                if not ds.get_changed():
                    if len(ds) - 1 > self._nfe[currentds]:
                        print("***WARNING: More finite elements were found in "
                              "ContinuousSet '%s' than the number of finite "
                              "elements specified in apply. The larger number "
                              "of finite elements will be used." % ds.name)

                self._nfe[ds.name] = len(ds) - 1
                self._fe[ds.name] = sorted(ds)
                # Adding discretization information to the differentialset
                # object itself so that it can be accessed outside of the
                # discretization object
                disc_info = ds.get_discretization_info()
                disc_info['nfe'] = self._nfe[ds.name]
                disc_info['scheme'] = self._scheme_name + ' Difference'

        # Maybe check to see if any of the ContinuousSets have been changed,
        # if they haven't then the model components need not be updated
        # or even iterated through
        expand_components(block)

        for d in block.component_objects(DerivativeVar, descend_into=True):
            dsets = d.get_continuousset_list()
            for i in set(dsets):
                if currentds is None or i.name == currentds:
                    oldexpr = d.get_derivative_expression()
                    loc = d.get_state_var()._contset[i]
                    count = dsets.count(i)
                    if count >= 3:
                        raise DAE_Error(
                            "Error discretizing '%s' with respect to '%s'. "
                            "Current implementation only allows for taking the"
                            " first or second derivative with respect to "
                            "a particular ContinuousSet" % (d.name, i.name))
                    scheme = self._scheme[count - 1]
                    newexpr = create_partial_expression(scheme, oldexpr, i,
                                                        loc)
                    d.set_derivative_expression(newexpr)

            # Reclassify DerivativeVar if all indexing ContinuousSets have
            # been discretized. Add discretization equations to the
            # DerivativeVar's parent block.
            if d.is_fully_discretized():
                add_discretization_equations(d.parent_block(), d)
                d.parent_block().reclassify_component_type(d, Var)

        # Reclassify Integrals if all ContinuousSets have been discretized
        if block_fully_discretized(block):

            if block.contains_component(Integral):
                for i in block.component_objects(Integral, descend_into=True):
                    i.reconstruct()
                    i.parent_block().reclassify_component_type(i, Expression)
                # If a model contains integrals they are most likely to
                # appear in the objective function which will need to be
                # reconstructed after the model is discretized.
                for k in block.component_objects(Objective, descend_into=True):
                    # TODO: check this, reconstruct might not work
                    k.reconstruct()