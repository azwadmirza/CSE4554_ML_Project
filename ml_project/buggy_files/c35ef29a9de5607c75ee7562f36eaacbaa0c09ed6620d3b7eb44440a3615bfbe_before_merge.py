def add_assets(path, quality=1.0, use_data_dir=False, rel_path=False):
    if not bpy.data.worlds['Arm'].arm_minimize and path.endswith('.arm'):
        path = path[:-4] + '.json'

    if rel_path:
        path = os.path.relpath(path, arm.utils.get_fp()).replace('\\', '/')

    notinlist = not path.endswith('.ttf') # TODO
    s = 'project.addAssets("' + path + '", { notinlist: ' + str(notinlist).lower() + ' '
    if quality < 1.0:
        s += ', quality: ' + str(quality)
    if use_data_dir:
        s += ', destination: "data/{name}"'
    s += '});\n'
    return s