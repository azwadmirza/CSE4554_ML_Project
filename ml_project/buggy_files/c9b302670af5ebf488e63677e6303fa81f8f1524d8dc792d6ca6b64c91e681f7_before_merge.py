    def get_deps_from_req(cls, req, resolver=None):
        # type: (Requirement, Optional["Resolver"]) -> Tuple[Set[str], Dict[str, Dict[str, Union[str, bool, List[str]]]]]
        from .vendor.requirementslib.models.utils import _requirement_to_str_lowercase_name
        from .vendor.requirementslib.models.requirements import Requirement
        from requirementslib.utils import is_installable_dir
        # TODO: this is way too complex, refactor this
        constraints = set()  # type: Set[str]
        locked_deps = dict()  # type: Dict[str, Dict[str, Union[str, bool, List[str]]]]
        if (req.is_file_or_url or req.is_vcs) and not req.is_wheel:
            # for local packages with setup.py files and potential direct url deps:
            if req.is_vcs:
                req_list, lockfile = get_vcs_deps(reqs=[req])
                req = next(iter(req for req in req_list if req is not None), req_list)
                entry = lockfile[pep423_name(req.normalized_name)]
            else:
                _, entry = req.pipfile_entry
            parsed_line = req.req.parsed_line  # type: Line
            setup_info = None  # type: Any
            try:
                name = req.normalized_name
            except TypeError:
                raise RequirementError(req=req)
            setup_info = req.req.setup_info
            setup_info.get_info()
            locked_deps[pep423_name(name)] = entry
            requirements = []
            # Allow users to toggle resolution off for non-editable VCS packages
            # but leave it on for local, installable folders on the filesystem
            if environments.PIPENV_RESOLVE_VCS or (
                req.editable or parsed_line.is_wheel or (
                    req.is_file_or_url and parsed_line.is_local
                    and is_installable_dir(parsed_line.path)
                )
            ):
                requirements = [v for v in getattr(setup_info, "requires", {}).values()]
            for r in requirements:
                if getattr(r, "url", None) and not getattr(r, "editable", False):
                    if r is not None:
                        if not r.url:
                            continue
                        line = _requirement_to_str_lowercase_name(r)
                        new_req, _, _ = cls.parse_line(line)
                        if r.marker and not r.marker.evaluate():
                            new_constraints = {}
                            _, new_entry = req.pipfile_entry
                            new_lock = {
                                pep423_name(new_req.normalized_name): new_entry
                            }
                        else:
                            new_constraints, new_lock = cls.get_deps_from_req(
                                new_req, resolver
                            )
                        locked_deps.update(new_lock)
                        constraints |= new_constraints
                # if there is no marker or there is a valid marker, add the constraint line
                elif r and (not r.marker or (r.marker and r.marker.evaluate())):
                    line = _requirement_to_str_lowercase_name(r)
                    constraints.add(line)
            # ensure the top level entry remains as provided
            # note that we shouldn't pin versions for editable vcs deps
            if not req.is_vcs:
                if req.specifiers:
                    locked_deps[name]["version"] = req.specifiers
                elif parsed_line.setup_info and parsed_line.setup_info.version:
                    locked_deps[name]["version"] = "=={}".format(
                        parsed_line.setup_info.version
                    )
            # if not req.is_vcs:
            locked_deps.update({name: entry})
            if req.is_vcs and req.editable:
                constraints.add(req.constraint_line)
            if req.is_file_or_url and req.req.is_local and req.editable and (
                    req.req.setup_path is not None and os.path.exists(req.req.setup_path)):
                constraints.add(req.constraint_line)
        else:
            # if the dependency isn't installable, don't add it to constraints
            # and instead add it directly to the lock
            if req and req.requirement and (
                req.requirement.marker and not req.requirement.marker.evaluate()
            ):
                pypi = resolver.repository if resolver else None
                best_match = pypi.find_best_match(req.ireq) if pypi else None
                if best_match:
                    hashes = resolver.collect_hashes(best_match) if resolver else []
                    new_req = Requirement.from_ireq(best_match)
                    new_req = new_req.add_hashes(hashes)
                    name, entry = new_req.pipfile_entry
                    locked_deps[pep423_name(name)] = translate_markers(entry)
                return constraints, locked_deps
            constraints.add(req.constraint_line)
            return constraints, locked_deps
        return constraints, locked_deps