def _init_envvars():
    """Initialize environment variables which need to be set early."""
    if (objects.backend == usertypes.Backend.QtWebEngine and
            config.val.qt.force_software_rendering):
        os.environ['QT_XCB_FORCE_SOFTWARE_OPENGL'] = '1'

    if config.val.qt.force_platform is not None:
        os.environ['QT_QPA_PLATFORM'] = config.val.qt.force_platform

    if config.val.window.hide_decoration:
        os.environ['QT_WAYLAND_DISABLE_WINDOWDECORATION'] = '1'

    if config.val.qt.highdpi:
        os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'