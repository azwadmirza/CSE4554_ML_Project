    def __init__(self, **kwds):
        GLGraphicsItem.__init__(self)
        glopts = kwds.pop('glOptions', 'additive')
        self.setGLOptions(glopts)
        self.pos = []
        self.size = 10
        self.color = [1.0,1.0,1.0,0.5]
        self.pxMode = True
        #self.vbo = {}      ## VBO does not appear to improve performance very much.
        self.setData(**kwds)
        self.shader = None