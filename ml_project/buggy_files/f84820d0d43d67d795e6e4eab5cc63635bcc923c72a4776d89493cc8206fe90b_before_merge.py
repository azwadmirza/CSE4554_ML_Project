    def _transform_constraint(self, obj, disjunct, bigMargs,
                              suffix_list):
        # add constraint to the transformation block, we'll transform it there.
        transBlock = disjunct._transformation_block()
        bigm_src = transBlock.bigm_src
        constraintMap = self._get_constraint_map_dict(transBlock)
        
        disjunctionRelaxationBlock = transBlock.parent_block()
        # Though rare, it is possible to get naming conflicts here
        # since constraints from all blocks are getting moved onto the
        # same block. So we get a unique name
        cons_name = obj.getname(fully_qualified=True, name_buffer=NAME_BUFFER)
        name = unique_component_name(transBlock, cons_name)

        if obj.is_indexed():
            try:
                newConstraint = Constraint(obj.index_set(),
                                           disjunctionRelaxationBlock.lbub)
            except TypeError:
                # The original constraint may have been indexed by a
                # non-concrete set (like an Any).  We will give up on
                # strict index verification and just blindly proceed.
                newConstraint = Constraint(Any)
        else:
            newConstraint = Constraint(disjunctionRelaxationBlock.lbub)
        transBlock.add_component(name, newConstraint)
        # add mapping of original constraint to transformed constraint
        constraintMap['srcConstraints'][newConstraint] = obj
        constraintMap['transformedConstraints'][obj] = newConstraint

        for i in sorted(iterkeys(obj)):
            c = obj[i]
            if not c.active:
                continue

            # first, we see if an M value was specified in the arguments.
            # (This returns None if not)
            M = self._get_M_from_args(c, bigMargs, bigm_src)

            if __debug__ and logger.isEnabledFor(logging.DEBUG):
                _name = obj.getname(
                    fully_qualified=True, name_buffer=NAME_BUFFER)
                logger.debug("GDP(BigM): The value for M for constraint %s "
                             "from the BigM argument is %s." % (cons_name,
                                                                str(M)))

            # if we didn't get something from args, try suffixes:
            if M is None:
                M = self._get_M_from_suffixes(c, suffix_list, bigm_src)

            if __debug__ and logger.isEnabledFor(logging.DEBUG):
                _name = obj.getname(
                    fully_qualified=True, name_buffer=NAME_BUFFER)
                logger.debug("GDP(BigM): The value for M for constraint %s "
                             "after checking suffixes is %s." % (cons_name,
                                                                 str(M)))

            if not isinstance(M, (tuple, list)):
                if M is None:
                    M = (None, None)
                else:
                    try:
                        M = (-M, M)
                    except:
                        logger.error("Error converting scalar M-value %s "
                                     "to (-M,M).  Is %s not a numeric type?"
                                     % (M, type(M)))
                        raise
            if len(M) != 2:
                raise GDP_Error("Big-M %s for constraint %s is not of "
                                "length two. "
                                "Expected either a single value or "
                                "tuple or list of length two for M."
                                % (str(M), name))

            if c.lower is not None and M[0] is None:
                M = (self._estimate_M(c.body, name)[0] - c.lower, M[1])
                bigm_src[c] = M
            if c.upper is not None and M[1] is None:
                M = (M[0], self._estimate_M(c.body, name)[1] - c.upper)
                bigm_src[c] = M

            if __debug__ and logger.isEnabledFor(logging.DEBUG):
                _name = obj.getname(
                    fully_qualified=True, name_buffer=NAME_BUFFER)
                logger.debug("GDP(BigM): The value for M for constraint %s "
                             "after estimating (if needed) is %s." %
                             (cons_name, str(M)))

            # Handle indices for both SimpleConstraint and IndexedConstraint
            if i.__class__ is tuple:
                i_lb = i + ('lb',)
                i_ub = i + ('ub',)
            elif obj.is_indexed():
                i_lb = (i, 'lb',)
                i_ub = (i, 'ub',)
            else:
                i_lb = 'lb'
                i_ub = 'ub'

            if c.lower is not None:
                if M[0] is None:
                    raise GDP_Error("Cannot relax disjunctive constraint %s "
                                    "because M is not defined." % name)
                M_expr = M[0] * (1 - disjunct.indicator_var)
                newConstraint.add(i_lb, c.lower <= c. body - M_expr)
            if c.upper is not None:
                if M[1] is None:
                    raise GDP_Error("Cannot relax disjunctive constraint %s "
                                    "because M is not defined." % name)
                M_expr = M[1] * (1 - disjunct.indicator_var)
                newConstraint.add(i_ub, c.body - M_expr <= c.upper)
            # deactivate because we relaxed
            c.deactivate()