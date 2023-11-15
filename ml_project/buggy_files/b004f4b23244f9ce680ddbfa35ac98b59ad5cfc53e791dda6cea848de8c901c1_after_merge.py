    def _warn_about_conflicts(self, to_install):
        try:
            package_set, _dep_info = check_install_conflicts(to_install)
        except Exception:
            logger.error("Error checking for conflicts.", exc_info=True)
            return
        missing, conflicting = _dep_info

        # NOTE: There is some duplication here from pip check
        for project_name in missing:
            version = package_set[project_name][0]
            for dependency in missing[project_name]:
                logger.critical(
                    "%s %s requires %s, which is not installed.",
                    project_name, version, dependency[1],
                )

        for project_name in conflicting:
            version = package_set[project_name][0]
            for dep_name, dep_version, req in conflicting[project_name]:
                logger.critical(
                    "%s %s has requirement %s, but you'll have %s %s which is "
                    "incompatible.",
                    project_name, version, req, dep_name, dep_version,
                )