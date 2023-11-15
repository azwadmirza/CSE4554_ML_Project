def _load_sound_library():
    """
    Special code for Windows so we grab the proper avbin from our directory.
    Otherwise hope the correct package is installed.
    """

    # lazy loading
    if not _load_sound_library._sound_library_loaded:
        _load_sound_library._sound_library_loaded = True
    else:
        return

    import os
    appveyor = not os.environ.get('APPVEYOR') is None

    import platform
    path_user = ""
    my_system = platform.system()
    if my_system == 'Windows':

        import sys
        is64bit = sys.maxsize > 2 ** 32

        import site
        if hasattr(site, 'getsitepackages'):
            packages = site.getsitepackages()
            user_packages = site.getuserbase()

            if appveyor:
                if is64bit:
                    path_global = "Win64/avbin"
                else:
                    path_global = "Win32/avbin"

            else:
                if is64bit:
                    path_global = packages[0] + "/lib/site-packages/arcade/Win64/avbin"
                    path_user = user_packages + "/lib/site-packages/arcade/Win64/avbin"
                else:
                    path_global = packages[0] + "/lib/site-packages/arcade/Win32/avbin"
                    path_user = user_packages + "/lib/site-packages/arcade/Win32/avbin"

        else:
            if is64bit:
                path_global = "Win64/avbin"
            else:
                path_global = "Win32/avbin"

    elif my_system == 'Darwin':
        from distutils.sysconfig import get_python_lib
        path_global = get_python_lib() + '/lib/site-packages/arcade/lib/libavbin.10.dylib'
        pyglet.options['audio'] = ('openal', 'pulse', 'silent')

    else:
        path_global = "avbin"
        pyglet.options['audio'] = ('openal', 'pulse', 'silent')

    pyglet.have_avbin = False
    try:
        pyglet.lib.load_library(path_user)
        pyglet.have_avbin = True
    except ImportError:
        pass

    if not pyglet.have_avbin:
        try:
            pyglet.lib.load_library(path_global)
            pyglet.have_avbin = True
        except ImportError:
            pass

    if not pyglet.have_avbin:
        # Try loading like its never been installed, from current directory.
        try:
            import platform
            mysys = platform.architecture()
            post = "avbin"
            if mysys[0] == '32bit':
                post = "/../Win32/avbin"
            elif mysys[0] == '64bit':
                post = "/../Win64/avbin"

            import os
            dir_path = os.path.dirname(os.path.realpath(__file__)) + post
            pyglet.lib.load_library(dir_path)
            pyglet.have_avbin = True
        except ImportError:
            pass

    if not pyglet.have_avbin:
        print("Warning - Unable to load sound library.")