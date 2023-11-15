def _fetch_modules(package):
    modules = [package]
    for module_info in pkgutil.walk_packages(
            path=package.__path__,
            prefix=package.__name__ + '.',
    ):
        module = importlib.import_module(module_info.name)
        modules.append(module)
    return modules