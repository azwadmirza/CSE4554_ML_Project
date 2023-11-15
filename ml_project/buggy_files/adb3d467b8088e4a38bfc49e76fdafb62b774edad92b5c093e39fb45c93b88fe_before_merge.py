    def install(self, spec, prefix):
        env['GEOS_DIR'] = spec['geos'].prefix
        setup_py('install', '--prefix=%s' % prefix)