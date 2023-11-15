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

            # Find all the .so files in app and app_packages,
            # so they can be passed in to linuxdeploy to have their
            # dependencies added to the AppImage. Looks for any .so file
            # in the application, and make sure it is marked for deployment.
            so_folders = set()
            for so_file in self.appdir_path(app).glob('**/*.so'):
                so_folders.add(so_file.parent)

            deploy_deps_args = []
            for folder in sorted(so_folders):
                deploy_deps_args.extend(["--deploy-deps-only", str(folder)])

            # Build the app image. We use `--appimage-extract-and-run`
            # because AppImages won't run natively inside Docker.
            with self.dockerize(app) as docker:
                docker.run(
                    [
                        str(self.linuxdeploy_appimage_path),
                        "--appimage-extract-and-run",
                        "--appdir={appdir_path}".format(appdir_path=self.appdir_path(app)),
                        "-d", str(
                            self.appdir_path(app) / "{app.bundle}.{app.app_name}.desktop".format(
                                app=app,
                            )
                        ),
                        "-o", "appimage",
                    ] + deploy_deps_args,
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