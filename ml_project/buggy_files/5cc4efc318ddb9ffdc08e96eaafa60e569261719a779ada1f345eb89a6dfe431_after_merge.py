def get_versions(reporev=True):
    """Get version information for components used by Spyder"""
    import sys
    import platform
    import spyderlib.qt
    import spyderlib.qt.QtCore

    revision = None
    if reporev:
        from spyderlib.utils import vcs
        revision = vcs.get_git_revision(os.path.dirname(__dir__))

    if not sys.platform == 'darwin':  # To avoid a crash with our Mac app
        system = platform.system()
    else:
        system = 'Darwin'
    
    return {
        'spyder': __version__,
        'python': platform.python_version(),  # "2.7.3"
        'bitness': 64 if sys.maxsize > 2**32 else 32,
        'qt': spyderlib.qt.QtCore.__version__,
        'qt_api': spyderlib.qt.API_NAME,      # PySide or PyQt4
        'qt_api_ver': spyderlib.qt.__version__,
        'system': system,   # Linux, Windows, ...
        'revision': revision,  # '9fdf926eccce'
    }