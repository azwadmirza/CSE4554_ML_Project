def check_roslaunch(f, use_test_depends=False):
    """
    Check roslaunch file for errors, returning error message if check fails. This routine
    is mainly to support rostest's roslaunch_check.

    :param f: roslaunch file name, ``str``
    :param use_test_depends: Consider test_depends, ``Bool``
    :returns: error message or ``None``
    """
    try:
        rl_config = roslaunch.config.load_config_default([f], DEFAULT_MASTER_PORT, verbose=False)
    except roslaunch.core.RLException as e:
        return str(e)
    
    rospack = rospkg.RosPack()
    errors = []
    # check for missing deps
    try:
        base_pkg, file_deps, missing = roslaunch.depends.roslaunch_deps([f], use_test_depends=use_test_depends)
    except rospkg.common.ResourceNotFound as r:
        errors.append("Could not find package [%s] included from [%s]"%(str(r), f))
        missing = {}
        file_deps = {}
    except roslaunch.substitution_args.ArgException as e:
        errors.append("Could not resolve arg [%s] in [%s]"%(str(e), f))
        missing = {}
        file_deps = {}
    for pkg, miss in missing.items():
        # even if the pkgs is not found in packges.xml, if other package.xml provdes that pkgs, then it will be ok
        all_pkgs = []
        try:
            for file_dep in file_deps.keys():
                file_pkg = rospkg.get_package_name(file_dep)
                all_pkgs.extend(rospack.get_depends(file_pkg,implicit=False))
                miss_all = list(set(miss) - set(all_pkgs))
        except Exception as e:
            print(e, file=sys.stderr)
            miss_all = True
        if miss_all:
            print("Missing package dependencies: %s/package.xml: %s"%(pkg, ', '.join(miss)), file=sys.stderr)
            errors.append("Missing package dependencies: %s/package.xml: %s"%(pkg, ', '.join(miss)))
        elif miss:
            print("Missing package dependencies: %s/package.xml: %s (notify upstream maintainer)"%(pkg, ', '.join(miss)), file=sys.stderr)
    
    # load all node defs
    nodes = []
    for filename, rldeps in file_deps.items():
        nodes.extend(rldeps.nodes)

    # check for missing packages
    for pkg, node_type in nodes:
        try:
            rospack.get_path(pkg)
        except:
            errors.append("cannot find package [%s] for node [%s]"%(pkg, node_type))

    # check for missing nodes
    for pkg, node_type in nodes:
        try:
            if not roslib.packages.find_node(pkg, node_type, rospack=rospack):
                errors.append("cannot find node [%s] in package [%s]"%(node_type, pkg))
        except Exception as e:
            errors.append("unable to find node [%s/%s]: %s"%(pkg, node_type, str(e)))
                
    # Check for configuration errors, #2889
    for err in rl_config.config_errors:
        errors.append('ROSLaunch config error: %s' % err)

    if errors:
        return '\n'.join(errors)