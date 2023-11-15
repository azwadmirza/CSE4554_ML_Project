def vcvars_dict(settings, arch=None, compiler_version=None, force=False, filter_known_paths=False,
                vcvars_ver=None, winsdk_version=None, only_diff=True):
    known_path_lists = ("include", "lib", "libpath", "path")
    cmd = vcvars_command(settings, arch=arch,
                         compiler_version=compiler_version, force=force,
                         vcvars_ver=vcvars_ver, winsdk_version=winsdk_version)
    cmd += " && echo __BEGINS__ && set"
    ret = decode_text(subprocess.check_output(cmd, shell=True))
    new_env = {}
    start_reached = False
    for line in ret.splitlines():
        line = line.strip()
        if not start_reached:
            if "__BEGINS__" in line:
                start_reached = True
            continue

        if line == "\n" or not line:
            continue
        try:
            name_var, value = line.split("=", 1)
            new_value = value.split(os.pathsep) if name_var.lower() in known_path_lists else value
            # Return only new vars & changed ones, but only with the changed elements if the var is
            # a list
            if only_diff:
                old_value = os.environ.get(name_var)
                if name_var.lower() == "path":
                    old_values_lower = [v.lower() for v in old_value.split(os.pathsep)]
                    # Clean all repeated entries, not append if the element was already there
                    new_env[name_var] = [v for v in new_value if v.lower() not in old_values_lower]
                elif old_value and value.endswith(os.pathsep + old_value):
                    # The new value ends with separator and the old value, is a list,
                    # get only the new elements
                    new_env[name_var] = value[:-(len(old_value) + 1)].split(os.pathsep)
                elif value != old_value:
                    # Only if the vcvars changed something, we return the variable,
                    # otherwise is not vcvars related
                    new_env[name_var] = new_value
            else:
                new_env[name_var] = new_value

        except ValueError:
            pass

    if filter_known_paths:
        def relevant_path(path):
            path = path.replace("\\", "/").lower()
            keywords = "msbuild", "visual", "microsoft", "/msvc/", "/vc/", "system32", "windows"
            return any(word in path for word in keywords)

        path_key = next((name for name in new_env.keys() if "path" == name.lower()), None)
        if path_key:
            path = [entry for entry in new_env.get(path_key, "") if relevant_path(entry)]
            new_env[path_key] = ";".join(path)

    return new_env