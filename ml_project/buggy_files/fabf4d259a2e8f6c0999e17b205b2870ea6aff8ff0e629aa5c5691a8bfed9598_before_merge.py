    def __init__(self):
        app.Canvas.__init__(self, title='Use your wheel to zoom!', 
                            keys='interactive')
        self.program = gloo.Program(VERT_SHADER, FRAG_SHADER)
        self.program['a_position'] = y.ravel()
        self.program['a_color'] = color
        self.program['a_index'] = index
        self.program['u_scale'] = (1., 1.)
        self.program['u_size'] = (nrows, ncols)
        self.program['u_n'] = n
        
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)