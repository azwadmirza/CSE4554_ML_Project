    def compile_pillar(self, ext=True, pillar_dirs=None):
        ret = super(AsyncPillar, self).compile_pillar(ext=ext, pillar_dirs=pillar_dirs)
        raise tornado.gen.Return(ret)