    def solve_final_state(self, deps_modifier=NULL, prune=NULL, ignore_pinned=NULL,
                          force_remove=NULL):
        """Gives the final, solved state of the environment.

        Args:
            deps_modifier (DepsModifier):
                An optional flag indicating special solver handling for dependencies. The
                default solver behavior is to be as conservative as possible with dependency
                updates (in the case the dependency already exists in the environment), while
                still ensuring all dependencies are satisfied.  Options include
                    * NO_DEPS
                    * ONLY_DEPS
                    * UPDATE_DEPS
                    * UPDATE_DEPS_ONLY_DEPS
            prune (bool):
                If ``True``, the solution will not contain packages that were
                previously brought into the environment as dependencies but are no longer
                required as dependencies and are not user-requested.
            ignore_pinned (bool):
                If ``True``, the solution will ignore pinned package configuration
                for the prefix.
            force_remove (bool):
                Forces removal of a package without removing packages that depend on it.

        Returns:
            Tuple[PackageRef]:
                In sorted dependency order from roots to leaves, the package references for
                the solved state of the environment.

        """
        prune = context.prune if prune is NULL else prune
        ignore_pinned = context.ignore_pinned if ignore_pinned is NULL else ignore_pinned
        deps_modifier = context.deps_modifier if deps_modifier is NULL else deps_modifier
        if isinstance(deps_modifier, string_types):
            deps_modifier = DepsModifier(deps_modifier.lower())
        specs_to_remove = self.specs_to_remove
        specs_to_add = self.specs_to_add

        # force_remove is a special case where we return early
        if specs_to_remove and force_remove:
            if specs_to_add:
                raise NotImplementedError()
            index, r = self._prepare(specs_to_remove)
            solution = tuple(Dist(rec) for rec in PrefixData(self.prefix).iter_records()
                             if not any(spec.match(rec) for spec in specs_to_remove))
            return IndexedSet(index[d] for d in r.dependency_sort({d.name: d for d in solution}))

        log.debug("solving prefix %s\n"
                  "  specs_to_remove: %s\n"
                  "  specs_to_add: %s\n"
                  "  prune: %s", self.prefix, specs_to_remove, specs_to_add, prune)

        # declare starting point, the initial state of the environment
        # `solution` and `specs_map` are mutated throughout this method
        prefix_data = PrefixData(self.prefix)
        solution = tuple(Dist(d) for d in prefix_data.iter_records())
        specs_from_history_map = History(self.prefix).get_requested_specs_map()
        if prune or deps_modifier == DepsModifier.UPDATE_ALL:
            # Start with empty specs map for UPDATE_ALL because we're optimizing the update
            # only for specs the user has requested; it's ok to remove dependencies.
            specs_map = odict()

            # However, because of https://github.com/conda/constructor/issues/138, we need
            # to hard-code keeping conda, conda-build, and anaconda, if they're already in
            # the environment.
            solution_pkg_names = set(d.name for d in solution)
            ensure_these = (pkg_name for pkg_name in {
                'anaconda', 'conda', 'conda-build',
            } if pkg_name not in specs_from_history_map and pkg_name in solution_pkg_names)
            for pkg_name in ensure_these:
                specs_from_history_map[pkg_name] = MatchSpec(pkg_name)
        else:
            specs_map = odict((d.name, MatchSpec(d.name)) for d in solution)

        # add in historically-requested specs
        specs_map.update(specs_from_history_map)

        # let's pretend for now that this is the right place to build the index
        prepared_specs = set(concatv(
            specs_to_remove,
            specs_to_add,
            itervalues(specs_from_history_map),
        ))

        index, r = self._prepare(prepared_specs)

        if specs_to_remove:
            # In a previous implementation, we invoked SAT here via `r.remove()` to help with
            # spec removal, and then later invoking SAT again via `r.solve()`. Rather than invoking
            # SAT for spec removal determination, we can use the DAG and simple tree traversal
            # if we're careful about how we handle features. We still invoke sat via `r.solve()`
            # later.
            _track_fts_specs = (spec for spec in specs_to_remove if 'track_features' in spec)
            feature_names = set(concat(spec.get_raw_value('track_features')
                                       for spec in _track_fts_specs))
            dag = PrefixDag((index[dist] for dist in solution), itervalues(specs_map))

            removed_records = []
            for spec in specs_to_remove:
                # If the spec was a provides_features spec, then we need to also remove every
                # package with a requires_feature that matches the provides_feature.  The
                # `dag.remove_spec()` method handles that for us.
                log.trace("using dag to remove records for %s", spec)
                removed_records.extend(dag.remove_spec(spec))

            for rec in removed_records:
                # We keep specs (minus the feature part) for the non provides_features packages
                # if they're in the history specs.  Otherwise, we pop them from the specs_map.
                rec_has_a_feature = set(rec.features or ()) & feature_names
                if rec_has_a_feature and rec.name in specs_from_history_map:
                    spec = specs_map.get(rec.name, MatchSpec(rec.name))
                    spec._match_components.pop('features', None)
                    specs_map[spec.name] = spec
                else:
                    specs_map.pop(rec.name, None)

            solution = tuple(Dist(rec) for rec in dag.records)

            if not removed_records and not prune:
                raise PackagesNotFoundError(tuple(spec.name for spec in specs_to_remove))

        # We handle as best as possible environments in inconsistent states. To do this,
        # we remove now from consideration the set of packages causing inconsistencies,
        # and then we add them back in following the main SAT call.
        _, inconsistent_dists = r.bad_installed(solution, ())
        add_back_map = {}  # name: (dist, spec)
        if log.isEnabledFor(DEBUG):
            log.debug("inconsistent dists: %s",
                      dashlist(inconsistent_dists) if inconsistent_dists else 'None')
        if inconsistent_dists:
            for dist in inconsistent_dists:
                # pop and save matching spec in specs_map
                add_back_map[dist.name] = (dist, specs_map.pop(dist.name, None))
            solution = tuple(dist for dist in solution if dist not in inconsistent_dists)

        # For the remaining specs in specs_map, add target to each spec. `target` is a reference
        # to the package currently existing in the environment. Setting target instructs the
        # solver to not disturb that package if it's not necessary.
        # If the spec.name is being modified by inclusion in specs_to_add, we don't set `target`,
        # since we *want* the solver to modify/update that package.
        #
        # TLDR: when working with MatchSpec objects,
        #  - to minimize the version change, set MatchSpec(name=name, target=dist.full_name)
        #  - to freeze the package, set all the components of MatchSpec individually
        for pkg_name, spec in iteritems(specs_map):
            matches_for_spec = tuple(dist for dist in solution if spec.match(index[dist]))
            if matches_for_spec:
                if len(matches_for_spec) != 1:
                    raise CondaError(dals("""
                    Conda encountered an error with your environment.  Please report an issue
                    at https://github.com/conda/conda/issues/new.  In your report, please include
                    the output of 'conda info' and 'conda list' for the active environment, along
                    with the command you invoked that resulted in this error.
                      matches_for_spec: %s
                    """) % matches_for_spec)
                target_dist = matches_for_spec[0]
                if deps_modifier == DepsModifier.FREEZE_INSTALLED:
                    new_spec = MatchSpec(index[target_dist])
                else:
                    target = Dist(target_dist).full_name
                    new_spec = MatchSpec(spec, target=target)
                specs_map[pkg_name] = new_spec
        if log.isEnabledFor(TRACE):
            log.trace("specs_map with targets: %s", specs_map)

        # If we're in UPDATE_ALL mode, we need to drop all the constraints attached to specs,
        # so they can all float and the solver can find the most up-to-date solution. In the case
        # of UPDATE_ALL, `specs_map` wasn't initialized with packages from the current environment,
        # but *only* historically-requested specs.  This lets UPDATE_ALL drop dependencies if
        # they're no longer needed, and their presence would otherwise prevent the updated solution
        # the user most likely wants.
        if deps_modifier == DepsModifier.UPDATE_ALL:
            specs_map = {pkg_name: MatchSpec(spec.name, optional=spec.optional)
                         for pkg_name, spec in iteritems(specs_map)}
            # The anaconda spec is a special case here, because of the 'custom' version.
            # Because of https://github.com/conda/conda/issues/6350, and until we implement
            # something like https://github.com/ContinuumIO/anaconda-issues/issues/4298, I think
            # this is the best we're going to do.
            if 'anaconda' in specs_map:
                specs_map['anaconda'] = MatchSpec('anaconda>1')

        # As a business rule, we never want to update python beyond the current minor version,
        # unless that's requested explicitly by the user (which we actively discourage).
        if 'python' in specs_map:
            python_prefix_rec = prefix_data.get('python')
            if python_prefix_rec:
                python_spec = specs_map['python']
                if not python_spec.get('version'):
                    pinned_version = get_major_minor_version(python_prefix_rec.version) + '.*'
                    specs_map['python'] = MatchSpec(python_spec, version=pinned_version)

        # For the aggressive_update_packages configuration parameter, we strip any target
        # that's been set.
        if not context.offline:
            for spec in context.aggressive_update_packages:
                if spec.name in specs_map:
                    old_spec = specs_map[spec.name]
                    specs_map[spec.name] = MatchSpec(old_spec, target=None)
            if (context.auto_update_conda and paths_equal(self.prefix, context.root_prefix)
                    and any(dist.name == "conda" for dist in solution)):
                specs_map["conda"] = MatchSpec("conda")

        # add in explicitly requested specs from specs_to_add
        # this overrides any name-matching spec already in the spec map
        specs_map.update((s.name, s) for s in specs_to_add)

        # collect additional specs to add to the solution
        track_features_specs = pinned_specs = ()
        if context.track_features:
            track_features_specs = tuple(MatchSpec(x + '@') for x in context.track_features)
        if not ignore_pinned:
            pinned_specs = get_pinned_specs(self.prefix)

        final_environment_specs = IndexedSet(concatv(
            itervalues(specs_map),
            track_features_specs,
            pinned_specs,
        ))

        # We've previously checked `solution` for consistency (which at that point was the
        # pre-solve state of the environment). Now we check our compiled set of
        # `final_environment_specs` for the possibility of a solution.  If there are conflicts,
        # we can often avoid them by neutering specs that have a target (e.g. removing version
        # constraint) and also making them optional. The result here will be less cases of
        # `UnsatisfiableError` handed to users, at the cost of more packages being modified
        # or removed from the environment.
        conflicting_specs = r.get_conflicting_specs(tuple(final_environment_specs))
        if log.isEnabledFor(DEBUG):
            log.debug("conflicting specs: %s", dashlist(conflicting_specs))
        for spec in conflicting_specs:
            if spec.target:
                final_environment_specs.remove(spec)
                neutered_spec = MatchSpec(spec.name, target=spec.target, optional=True)
                final_environment_specs.add(neutered_spec)

        # Finally! We get to call SAT.
        if log.isEnabledFor(DEBUG):
            log.debug("final specs to add: %s",
                      dashlist(sorted(text_type(s) for s in final_environment_specs)))
        solution = r.solve(tuple(final_environment_specs))  # return value is List[dist]

        # add back inconsistent packages to solution
        if add_back_map:
            for name, (dist, spec) in iteritems(add_back_map):
                if not any(d.name == name for d in solution):
                    solution.append(dist)
                    if spec:
                        final_environment_specs.add(spec)

        # Special case handling for various DepsModifer flags. Maybe this block could be pulled
        # out into its own non-public helper method?
        if deps_modifier == DepsModifier.NO_DEPS:
            # In the NO_DEPS case, we need to start with the original list of packages in the
            # environment, and then only modify packages that match specs_to_add or
            # specs_to_remove.
            _no_deps_solution = IndexedSet(Dist(rec) for rec in prefix_data.iter_records())
            only_remove_these = set(dist
                                    for spec in specs_to_remove
                                    for dist in _no_deps_solution
                                    if spec.match(index[dist]))
            _no_deps_solution -= only_remove_these

            only_add_these = set(dist
                                 for spec in specs_to_add
                                 for dist in solution
                                 if spec.match(index[dist]))
            remove_before_adding_back = set(dist.name for dist in only_add_these)
            _no_deps_solution = IndexedSet(dist for dist in _no_deps_solution
                                           if dist.name not in remove_before_adding_back)
            _no_deps_solution |= only_add_these
            solution = _no_deps_solution
        elif deps_modifier == DepsModifier.ONLY_DEPS:
            # Using a special instance of the DAG to remove leaf nodes that match the original
            # specs_to_add.  It's important to only remove leaf nodes, because a typical use
            # might be `conda install --only-deps python=2 flask`, and in that case we'd want
            # to keep python.
            dag = PrefixDag((index[d] for d in solution), specs_to_add)
            dag.remove_leaf_nodes_with_specs()
            solution = tuple(Dist(rec) for rec in dag.records)
        elif deps_modifier in (DepsModifier.UPDATE_DEPS, DepsModifier.UPDATE_DEPS_ONLY_DEPS):
            # Here we have to SAT solve again :(  It's only now that we know the dependency
            # chain of specs_to_add.
            specs_to_add_names = set(spec.name for spec in specs_to_add)
            update_names = set()
            dag = PrefixDag((index[d] for d in solution), final_environment_specs)
            for spec in specs_to_add:
                node = dag.get_node_by_name(spec.name)
                for ascendant in node.all_ascendants():
                    ascendant_name = ascendant.record.name
                    if ascendant_name not in specs_to_add_names:
                        update_names.add(ascendant_name)
            grouped_specs = groupby(lambda s: s.name in update_names, final_environment_specs)
            new_final_environment_specs = set(grouped_specs[False])
            update_specs = set(MatchSpec(spec.name, optional=spec.optional)
                               for spec in grouped_specs[True])
            final_environment_specs = new_final_environment_specs | update_specs
            solution = r.solve(final_environment_specs)

            if deps_modifier == DepsModifier.UPDATE_DEPS_ONLY_DEPS:
                # duplicated from DepsModifier.ONLY_DEPS
                dag = PrefixDag((index[d] for d in solution), specs_to_add)
                dag.remove_leaf_nodes_with_specs()
                solution = tuple(Dist(rec) for rec in dag.records)

        if prune:
            dag = PrefixDag((index[d] for d in solution), final_environment_specs)
            dag.prune()
            solution = tuple(Dist(rec) for rec in dag.records)

        self._check_solution(solution, pinned_specs)

        solution = IndexedSet(r.dependency_sort({d.name: d for d in solution}))
        log.debug("solved prefix %s\n"
                  "  solved_linked_dists:\n"
                  "    %s\n",
                  self.prefix, "\n    ".join(text_type(d) for d in solution))
        return IndexedSet(index[d] for d in solution)