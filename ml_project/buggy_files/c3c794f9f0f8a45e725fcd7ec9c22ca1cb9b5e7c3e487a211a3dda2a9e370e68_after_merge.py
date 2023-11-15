def add_shaders(path: str, rel_path=False) -> str:
    if rel_path:
        path = os.path.relpath(path, arm.utils.get_fp())
    return 'project.addShaders("' + path.replace('\\', '/').replace('//', '/') + '");\n'