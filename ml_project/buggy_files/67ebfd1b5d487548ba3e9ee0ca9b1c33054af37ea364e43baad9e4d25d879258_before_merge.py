def do_yarn_install(
    target_path: str,
    yarn_args: List[str],
    success_stamp: str,
    stdout: Optional[IO[Any]] = None,
    stderr: Optional[IO[Any]] = None,
) -> None:
    os.makedirs(target_path, exist_ok=True)
    shutil.copy('package.json', target_path)
    shutil.copy("yarn.lock", target_path)
    shutil.copy(".yarnrc", target_path)
    cached_node_modules = os.path.join(target_path, 'node_modules')
    print("Cached version not found! Installing node modules.")

    # Copy the existing node_modules to speed up install
    if os.path.exists("node_modules") and not os.path.exists(cached_node_modules):
        shutil.copytree("node_modules/", cached_node_modules, symlinks=True)
    if os.environ.get('CUSTOM_CA_CERTIFICATES'):
        run([YARN_BIN, "config", "set", "cafile", os.environ['CUSTOM_CA_CERTIFICATES']],
            stdout=stdout, stderr=stderr)
    run([YARN_BIN, "install", "--non-interactive", "--frozen-lockfile"] + yarn_args,
        cwd=target_path, stdout=stdout, stderr=stderr)
    with open(success_stamp, 'w'):
        pass