def add_armory_library(sdk_path, name, rel_path=False):
    if rel_path:
        sdk_path = '../' + os.path.relpath(sdk_path, arm.utils.get_fp()).replace('\\', '/')
    return ('project.addLibrary("' + sdk_path + '/' + name + '");\n').replace('\\', '/').replace('//', '/')