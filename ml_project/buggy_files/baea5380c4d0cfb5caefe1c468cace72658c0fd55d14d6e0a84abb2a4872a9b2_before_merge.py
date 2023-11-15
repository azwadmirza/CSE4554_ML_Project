    def _group_constraints(self, constraints):
        """
        Groups constraints (remember, InstallRequirements!) by their key name,
        and combining their SpecifierSets into a single InstallRequirement per
        package.  For example, given the following constraints:

            Django<1.9,>=1.4.2
            django~=1.5
            Flask~=0.7

        This will be combined into a single entry per package:

            django~=1.5,<1.9,>=1.4.2
            flask~=0.7

        """
        for _, ireqs in full_groupby(constraints, key=_dep_key):
            ireqs = list(ireqs)
            editable_ireq = first(ireqs, key=lambda ireq: ireq.editable)
            if editable_ireq:
                yield editable_ireq  # ignore all the other specs: the editable one is the one that counts
                continue

            ireqs = iter(ireqs)
            # deepcopy the accumulator so as to not modify the self.our_constraints invariant
            combined_ireq = copy.deepcopy(next(ireqs))
            combined_ireq.comes_from = None
            for ireq in ireqs:
                # NOTE we may be losing some info on dropped reqs here
                combined_ireq.req.specifier &= ireq.req.specifier
                combined_ireq.constraint &= ireq.constraint
                # Return a sorted, de-duped tuple of extras
                combined_ireq.extras = tuple(sorted(set(tuple(combined_ireq.extras) + tuple(ireq.extras))))
            yield combined_ireq