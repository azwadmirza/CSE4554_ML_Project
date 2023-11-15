    def __init__(self, environment, kwargs):
        Dependency.__init__(self, 'qt5')
        self.name = 'qt5'
        self.root = '/usr'
        mods = kwargs.get('modules', [])
        self.cargs = []
        self.largs = []
        self.is_found = False
        if isinstance(mods, str):
            mods = [mods]
        if len(mods) == 0:
            raise DependencyException('No Qt5 modules specified.')
        type_text = 'native'
        if environment.is_cross_build() and kwargs.get('native', False):
            type_text = 'cross'
            self.pkgconfig_detect(mods, environment, kwargs)
        elif not environment.is_cross_build() and shutil.which('pkg-config') is not None:
            self.pkgconfig_detect(mods, environment, kwargs)
        elif shutil.which('qmake') is not None:
            self.qmake_detect(mods, kwargs)
        else:
            self.version = 'none'
        if not self.is_found:
            mlog.log('Qt5 %s dependency found: ' % type_text, mlog.red('NO'))
        else:
            mlog.log('Qt5 %s dependency found: ' % type_text, mlog.green('YES'))