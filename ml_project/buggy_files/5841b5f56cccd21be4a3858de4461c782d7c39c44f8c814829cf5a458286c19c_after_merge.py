    def get_package_from_directory(
        cls, directory, name=None
    ):  # type: (Path, Optional[str]) -> Package
        supports_poetry = False
        pyproject = directory.joinpath("pyproject.toml")
        if pyproject.exists():
            pyproject = TomlFile(pyproject)
            pyproject_content = pyproject.read()
            supports_poetry = (
                "tool" in pyproject_content and "poetry" in pyproject_content["tool"]
            )

        if supports_poetry:
            poetry = Factory().create_poetry(directory)

            pkg = poetry.package
            package = Package(pkg.name, pkg.version)

            for dep in pkg.requires:
                if not dep.is_optional():
                    package.requires.append(dep)

            for extra, deps in pkg.extras.items():
                if extra not in package.extras:
                    package.extras[extra] = []

                for dep in deps:
                    package.extras[extra].append(dep)

            package.python_versions = pkg.python_versions
        else:
            # Execute egg_info
            current_dir = os.getcwd()
            os.chdir(str(directory))

            try:
                cwd = directory
                venv = EnvManager().get(cwd)
                venv.run("python", "setup.py", "egg_info")
            except EnvCommandError:
                result = SetupReader.read_from_directory(directory)
                if not result["name"]:
                    # The name could not be determined
                    # We use the dependency name
                    result["name"] = name

                if not result["version"]:
                    # The version could not be determined
                    # so we raise an error since it is mandatory
                    raise RuntimeError(
                        "Unable to retrieve the package version for {}".format(
                            directory
                        )
                    )

                package_name = result["name"]
                package_version = result["version"]
                python_requires = result["python_requires"]
                if python_requires is None:
                    python_requires = "*"

                package_summary = ""

                requires = ""
                for dep in result["install_requires"]:
                    requires += dep + "\n"

                if result["extras_require"]:
                    requires += "\n"

                for extra_name, deps in result["extras_require"].items():
                    requires += "[{}]\n".format(extra_name)

                    for dep in deps:
                        requires += dep + "\n"

                    requires += "\n"

                reqs = parse_requires(requires)
            else:
                os.chdir(current_dir)
                # Sometimes pathlib will fail on recursive
                # symbolic links, so we need to workaround it
                # and use the glob module instead.
                # Note that this does not happen with pathlib2
                # so it's safe to use it for Python < 3.4.
                if PY35:
                    egg_info = next(
                        Path(p)
                        for p in glob.glob(
                            os.path.join(str(directory), "**", "*.egg-info"),
                            recursive=True,
                        )
                    )
                else:
                    egg_info = next(directory.glob("**/*.egg-info"))

                meta = pkginfo.UnpackedSDist(str(egg_info))
                package_name = meta.name
                package_version = meta.version
                package_summary = meta.summary
                python_requires = meta.requires_python

                if meta.requires_dist:
                    reqs = list(meta.requires_dist)
                else:
                    reqs = []
                    requires = egg_info / "requires.txt"
                    if requires.exists():
                        with requires.open(encoding="utf-8") as f:
                            reqs = parse_requires(f.read())
            finally:
                os.chdir(current_dir)

            package = Package(package_name, package_version)

            if name and name != package.name:
                # For now, the dependency's name must match the actual package's name
                raise RuntimeError(
                    "The dependency name for {} does not match the actual package's name: {}".format(
                        name, package_name
                    )
                )

            package.description = package_summary

            for req in reqs:
                dep = dependency_from_pep_508(req)
                if dep.in_extras:
                    for extra in dep.in_extras:
                        if extra not in package.extras:
                            package.extras[extra] = []

                        package.extras[extra].append(dep)

                if not dep.is_optional():
                    package.requires.append(dep)

            if python_requires:
                package.python_versions = python_requires

        package.source_type = "directory"
        package.source_url = directory.as_posix()

        return package