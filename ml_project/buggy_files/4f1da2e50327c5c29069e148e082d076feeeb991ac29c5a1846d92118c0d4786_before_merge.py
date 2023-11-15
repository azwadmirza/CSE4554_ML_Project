    def get_installation_error(self, e):
        # type: (ResolutionImpossible) -> InstallationError

        assert e.causes, "Installation error reported with no cause"

        # If one of the things we can't solve is "we need Python X.Y",
        # that is what we report.
        for cause in e.causes:
            if isinstance(cause.requirement, RequiresPythonRequirement):
                return self._report_requires_python_error(
                    cause.requirement,
                    cause.parent,
                )

        # Otherwise, we have a set of causes which can't all be satisfied
        # at once.

        # The simplest case is when we have *one* cause that can't be
        # satisfied. We just report that case.
        if len(e.causes) == 1:
            req, parent = e.causes[0]
            if parent is None:
                req_disp = str(req)
            else:
                req_disp = '{} (from {})'.format(req, parent.name)
            logger.critical(
                "Could not find a version that satisfies the requirement %s",
                req_disp,
            )
            return DistributionNotFound(
                'No matching distribution found for {}'.format(req)
            )

        # OK, we now have a list of requirements that can't all be
        # satisfied at once.

        # A couple of formatting helpers
        def text_join(parts):
            # type: (List[str]) -> str
            if len(parts) == 1:
                return parts[0]

            return ", ".join(parts[:-1]) + " and " + parts[-1]

        def readable_form(cand):
            # type: (Candidate) -> str
            return "{} {}".format(cand.name, cand.version)

        triggers = []
        for req, parent in e.causes:
            if parent is None:
                # This is a root requirement, so we can report it directly
                trigger = req.format_for_error()
            else:
                ireq = parent.get_install_requirement()
                if ireq and ireq.comes_from:
                    trigger = "{}".format(
                        ireq.comes_from.name
                    )
                else:
                    trigger = "{} {}".format(
                        parent.name,
                        parent.version
                    )
            triggers.append(trigger)

        if triggers:
            info = text_join(triggers)
        else:
            info = "the requested packages"

        msg = "Cannot install {} because these package versions " \
            "have conflicting dependencies.".format(info)
        logger.critical(msg)
        msg = "\nThe conflict is caused by:"
        for req, parent in e.causes:
            msg = msg + "\n    "
            if parent:
                msg = msg + "{} {} depends on ".format(
                    parent.name,
                    parent.version
                )
            else:
                msg = msg + "The user requested "
            msg = msg + req.format_for_error()

        msg = msg + "\n\n" + \
            "To fix this you could try to:\n" + \
            "1. loosen the range of package versions you've specified\n" + \
            "2. remove package versions to allow pip attempt to solve " + \
            "the dependency conflict\n"

        logger.info(msg)

        return DistributionNotFound(
            "ResolutionImpossible For help visit: "
            "https://pip.pypa.io/en/stable/user_guide/"
            "#fixing-conflicting-dependencies"
        )