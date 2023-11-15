    def handle(self):
        from clikit.utils.terminal import Terminal
        from poetry.repositories.installed_repository import InstalledRepository
        from poetry.semver import Version

        package = self.argument("package")

        if self.option("tree"):
            self.init_styles(self.io)

        if self.option("outdated"):
            self._args.set_option("latest", True)

        include_dev = not self.option("no-dev")
        locked_repo = self.poetry.locker.locked_repository(include_dev)

        # Show tree view if requested
        if self.option("tree") and not package:
            requires = self.poetry.package.requires + self.poetry.package.dev_requires
            packages = locked_repo.packages
            for package in packages:
                for require in requires:
                    if package.name == require.name:
                        self.display_package_tree(self._io, package, locked_repo)
                        break

            return 0

        table = self.table(style="compact")
        # table.style.line_vc_char = ""
        locked_packages = locked_repo.packages

        if package:
            pkg = None
            for locked in locked_packages:
                if package.lower() == locked.name:
                    pkg = locked
                    break

            if not pkg:
                raise ValueError("Package {} not found".format(package))

            if self.option("tree"):
                self.display_package_tree(self.io, pkg, locked_repo)

                return 0

            rows = [
                ["<info>name</>", " : <info>{}</>".format(pkg.pretty_name)],
                ["<info>version</>", " : <comment>{}</>".format(pkg.pretty_version)],
                ["<info>description</>", " : {}".format(pkg.description)],
            ]

            table.add_rows(rows)
            table.render(self.io)

            if pkg.requires:
                self.line("")
                self.line("<info>dependencies</info>")
                for dependency in pkg.requires:
                    self.line(
                        " - {} <comment>{}</>".format(
                            dependency.pretty_name, dependency.pretty_constraint
                        )
                    )

            return 0

        show_latest = self.option("latest")
        show_all = self.option("all")
        terminal = Terminal()
        width = terminal.width
        name_length = version_length = latest_length = 0
        latest_packages = {}
        latest_statuses = {}
        installed_repo = InstalledRepository.load(self.env)
        skipped = []

        python = Version.parse(".".join([str(i) for i in self.env.version_info[:3]]))

        # Computing widths
        for locked in locked_packages:
            python_constraint = locked.python_constraint
            if not python_constraint.allows(python) or not self.env.is_valid_for_marker(
                locked.marker
            ):
                skipped.append(locked)

                if not show_all:
                    continue

            current_length = len(locked.pretty_name)
            if not self._io.output.supports_ansi():
                installed_status = self.get_installed_status(locked, installed_repo)

                if installed_status == "not-installed":
                    current_length += 4

            if show_latest:
                latest = self.find_latest_package(locked, include_dev)
                if not latest:
                    latest = locked

                latest_packages[locked.pretty_name] = latest
                update_status = latest_statuses[
                    locked.pretty_name
                ] = self.get_update_status(latest, locked)

                if not self.option("outdated") or update_status != "up-to-date":
                    name_length = max(name_length, current_length)
                    version_length = max(
                        version_length, len(locked.full_pretty_version)
                    )
                    latest_length = max(latest_length, len(latest.full_pretty_version))
            else:
                name_length = max(name_length, current_length)
                version_length = max(version_length, len(locked.full_pretty_version))

        write_version = name_length + version_length + 3 <= width
        write_latest = name_length + version_length + latest_length + 3 <= width
        write_description = name_length + version_length + latest_length + 24 <= width

        for locked in locked_packages:
            color = "cyan"
            name = locked.pretty_name
            install_marker = ""
            if locked in skipped:
                if not show_all:
                    continue

                color = "black;options=bold"
            else:
                installed_status = self.get_installed_status(locked, installed_repo)
                if installed_status == "not-installed":
                    color = "red"

                    if not self._io.output.supports_ansi():
                        # Non installed in non decorated mode
                        install_marker = " (!)"

            line = "<fg={}>{:{}}{}</>".format(
                color, name, name_length - len(install_marker), install_marker
            )
            if write_version:
                line += " <b>{:{}}</b>".format(
                    locked.full_pretty_version, version_length
                )
            if show_latest:
                latest = latest_packages[locked.pretty_name]
                update_status = latest_statuses[locked.pretty_name]

                if self.option("outdated") and update_status == "up-to-date":
                    continue

                if write_latest:
                    color = "green"
                    if update_status == "semver-safe-update":
                        color = "red"
                    elif update_status == "update-possible":
                        color = "yellow"

                    line += " <fg={}>{:{}}</>".format(
                        color, latest.full_pretty_version, latest_length
                    )

            if write_description:
                description = locked.description
                remaining = width - name_length - version_length - 4
                if show_latest:
                    remaining -= latest_length

                if len(locked.description) > remaining:
                    description = description[: remaining - 3] + "..."

                line += " " + description

            self.line(line)