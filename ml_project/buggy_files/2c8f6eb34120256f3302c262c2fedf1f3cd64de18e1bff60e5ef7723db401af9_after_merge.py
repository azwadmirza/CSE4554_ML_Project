def get_build_requires(build_info, package_venv, setup_dir):
    with package_venv.new_action("get-build-requires", package_venv.envconfig.envdir) as action:
        result = package_venv._pcall(
            [
                package_venv.envconfig.envpython,
                BUILD_REQUIRE_SCRIPT,
                build_info.backend_module,
                build_info.backend_object,
                os.path.pathsep.join(str(p) for p in build_info.backend_paths),
            ],
            returnout=True,
            action=action,
            cwd=setup_dir,
        )
        return json.loads(result.split("\n")[-2])