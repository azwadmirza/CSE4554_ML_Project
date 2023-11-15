def add_shaders(path, rel_path=False):
    if rel_path:
        path = os.path.relpath(path, arm.utils.get_fp())
    return 'project.addShaders("' + path.replace('\\', '/').replace('//', '/') + '");\n'