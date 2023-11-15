def run(python_version, bitness, repo_root, entrypoint, package, icon_path,
        license_path, extra_packages=None, conda_path=None, suffix=None,
        template=None):
    """
    Run the installer generation.

    Given a certain python version, bitness, package repository root directory,
    package name, icon path and license path a pynsist configuration file
    (locking the dependencies set in setup.py) is generated and pynsist runned.
    """
    try:
        print("Setting up assets from", ASSETS_URL)
        print("Downloading assets from ", ASSETS_URL)
        filename = download_file(ASSETS_URL, 'installers/Windows/assets')

        print("Unzipping assets to", 'installers/Windows/assets')
        unzip_file(filename, 'installers/Windows/assets')

        with tempfile.TemporaryDirectory(
                prefix="installer-pynsist-") as work_dir:
            print("Temporary working directory at", work_dir)

            # NOTE: SHOULD BE TEMPORAL (until black has wheels available).
            # See the 'files' section on the pynsist template config too.
            print("Copying dist.info for black-20.8b1")
            shutil.copytree(
                "installers/Windows/assets/black/black-20.8b1.dist-info",
                os.path.join(work_dir, "black-20.8b1.dist-info"))

            # NOTE: SHOULD BE TEMPORAL (until jedi has the fix available).
            # See the 'files' section on the pynsist template config too.
            print("Copying patched CompiledSubprocess __main__.py for jedi")
            shutil.copy(
                "installers/Windows/assets/jedi/__main__.py",
                os.path.join(work_dir, "__main__.py"))

            print("Copying required assets for Tkinter to work")
            shutil.copytree(
                "installers/Windows/assets/tcl/lib",
                os.path.join(work_dir, "lib"))
            shutil.copy(
                "installers/Windows/assets/tcl/tcl86t.dll",
                os.path.join(work_dir, "tcl86t.dll"))
            shutil.copy(
                "installers/Windows/assets/tcl/tk86t.dll",
                os.path.join(work_dir, "tk86t.dll"))

            print("Copying NSIS plugins into discoverable path")
            shutil.copy(
                "installers/Windows/assets/nsist/plugins/x86-unicode/"
                "WinShell.dll",
                "C:/Program Files (x86)/NSIS/Plugins/x86-unicode/WinShell.dll")

            if template:
                print("Copying template into discoverable path for Pynsist")
                template_basename = os.path.basename(template)
                template_new_path = os.path.normpath(
                    os.path.join(
                        work_dir,
                        "packaging-env/Lib/site-packages/nsist"))
                os.makedirs(template_new_path)
                shutil.copy(
                    template,
                    os.path.join(template_new_path, template_basename))
                template = template_basename

            print("Creating the package virtual environment.")
            env_python = create_packaging_env(
                work_dir, python_version, conda_path=conda_path)

            print("Updating pip in the virtual environment", env_python)
            subprocess_run(
                [env_python, "-m", "pip", "install", "--upgrade", "pip",
                 "--no-warn-script-location"]
            )

            print("Updating setuptools in the virtual environment", env_python)
            subprocess_run(
                [env_python, "-m", "pip", "install", "--upgrade",
                 "--force-reinstall", "setuptools",
                 "--no-warn-script-location"]
            )

            print("Updating/installing wheel in the virtual environment",
                  env_python)
            subprocess_run(
                [env_python, "-m", "pip", "install", "--upgrade", "wheel",
                 "--no-warn-script-location"]
            )

            print("Installing package with", env_python)
            subprocess_run([env_python, "-m",
                            "pip", "install", repo_root,
                            "--no-warn-script-location"])

            if extra_packages:
                print("Installing extra packages.")
                subprocess_run([env_python, "-m", "pip", "install", "-r",
                                extra_packages, "--no-warn-script-location"])

            if INSTALL_EDITABLE_PACKAGES:
                print("Installing packages with the --editable flag")
                for e_package in INSTALL_EDITABLE_PACKAGES:
                    subprocess_run([env_python, "-m", "pip", "install", "-e",
                                    e_package, "--no-warn-script-location"])

            pynsist_cfg = os.path.join(work_dir, "pynsist.cfg")
            print("Creating pynsist configuration file", pynsist_cfg)
            installer_exe = create_pynsist_cfg(
                env_python, python_version, repo_root, entrypoint, package,
                icon_path, license_path, pynsist_cfg, extras=extra_packages,
                suffix=suffix, template=template)

            print("Installing pynsist.")
            subprocess_run([env_python, "-m", "pip", "install", PYNSIST_REQ,
                            "--no-warn-script-location"])

            print("Running pynsist.")
            subprocess_run([env_python, "-m", "nsist", pynsist_cfg])

            destination_dir = os.path.join(repo_root, "dist")
            print("Copying installer file to", destination_dir)
            os.makedirs(destination_dir, exist_ok=True)
            shutil.copy(
                os.path.join(work_dir, "build", "nsis", installer_exe),
                destination_dir,
            )
            print("Installer created!")
    except PermissionError:
        pass