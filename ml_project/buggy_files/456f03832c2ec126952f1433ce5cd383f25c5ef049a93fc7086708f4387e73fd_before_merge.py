    def build_app(self, app: BaseConfig, **kwargs):
        """
        Build an application.

        :param app: The application to build
        """
        print()
        print("[{app.app_name}] Building AppImage...".format(app=app))

        try:
            print()
            # Build the AppImage.
            # For some reason, the version has to be passed in as an
            # environment variable, *not* in the configuration...
            env = {
                'VERSION': app.version
            }
            appdir_path = self.bundle_path(app) / "{app.formal_name}.AppDir".format(
                app=app
            )
            with self.dockerize(app) as docker:
                docker.run(
                    [
                        str(self.linuxdeploy_appimage),
                        "--appimage-extract-and-run",
                        "--appdir={appdir_path}".format(appdir_path=appdir_path),
                        "-d", str(
                            appdir_path / "{app.bundle}.{app.app_name}.desktop".format(
                                app=app,
                            )
                        ),
                        "-o", "appimage",
                    ],
                    env=env,
                    check=True,
                    cwd=str(self.platform_path)
                )

            # Make the binary executable.
            self.os.chmod(str(self.binary_path(app)), 0o755)
        except subprocess.CalledProcessError:
            print()
            raise BriefcaseCommandError(
                "Error while building app {app.app_name}.".format(app=app)
            )