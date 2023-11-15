    def generate_package(self):
        build_file_subs = dict(
            changelog_version="{}-{}".format(self.chromium_version, self.release_revision),
            changelog_datetime=self._get_dpkg_changelog_datetime(),
            build_output=str(self.build_output),
            distribution_version=self._distro_version
        )
        self.logger.info("Building Debian package...")
        # TODO: Copy _dpkg_dir over each other in build/ similar to resource reading
        distutils.dir_util.copy_tree(str(self._dpkg_dir), str(self._sandbox_dpkg_dir))
        for old_path in self._sandbox_dpkg_dir.glob("*.in"):
            new_path = self._sandbox_dpkg_dir / old_path.stem
            old_path.replace(new_path)
            with new_path.open("r+") as new_file:
                content = self.BuildFileStringTemplate(new_file.read()).substitute(
                    **build_file_subs)
                new_file.seek(0)
                new_file.write(content)
                new_file.truncate()
        result = self._run_subprocess(["dpkg-buildpackage", "-b", "-uc"],
                                      cwd=str(self._sandbox_dir))
        if not result.returncode == 0:
            raise BuilderException("dpkg-buildpackage returned non-zero exit code: {}".format(
                result.returncode))