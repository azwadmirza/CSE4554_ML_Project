def main():
    package = sys.argv[1]
    bin_path = Path(sys.argv[2])

    apps = get_apps(package, bin_path)
    app_paths = [str(Path(bin_path) / app) for app in apps]
    app_paths_of_dependencies: Dict[str, List[str]] = {}
    app_paths_of_dependencies = _dfs_package_apps(
        bin_path, package, app_paths_of_dependencies
    )

    output = {
        "apps": apps,
        "app_paths": app_paths,
        "app_paths_of_dependencies": app_paths_of_dependencies,
        "package_version": get_package_version(package),
        "python_version": f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }

    print(json.dumps(output))