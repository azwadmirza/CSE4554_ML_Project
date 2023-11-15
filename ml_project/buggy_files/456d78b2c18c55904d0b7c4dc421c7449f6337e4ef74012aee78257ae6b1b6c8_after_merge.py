def init():
    """Initialize QtWebEngine-specific modules."""
    # For some reason we need to keep a reference, otherwise the scheme handler
    # won't work...
    # https://www.riverbankcomputing.com/pipermail/pyqt/2016-September/038075.html
    global _qute_scheme_handler

    app = QApplication.instance()
    log.init.debug("Initializing qute://* handler...")
    _qute_scheme_handler = webenginequtescheme.QuteSchemeHandler(parent=app)
    _qute_scheme_handler.install(webenginesettings.default_profile)
    _qute_scheme_handler.install(webenginesettings.private_profile)

    log.init.debug("Initializing request interceptor...")
    host_blocker = objreg.get('host-blocker')
    req_interceptor = interceptor.RequestInterceptor(
        host_blocker, parent=app)
    req_interceptor.install(webenginesettings.default_profile)
    req_interceptor.install(webenginesettings.private_profile)

    log.init.debug("Initializing QtWebEngine downloads...")
    download_manager = webenginedownloads.DownloadManager(parent=app)
    download_manager.install(webenginesettings.default_profile)
    download_manager.install(webenginesettings.private_profile)
    objreg.register('webengine-download-manager', download_manager)