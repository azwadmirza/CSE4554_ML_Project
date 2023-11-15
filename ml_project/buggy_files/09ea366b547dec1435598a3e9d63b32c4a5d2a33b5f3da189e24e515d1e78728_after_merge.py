    def __init__(self):
        app.Canvas.__init__(self, title='Spacy', keys='interactive')
        self.size = 800, 600
        
        self.program = gloo.Program(vertex, fragment)
        self.view = np.eye(4, dtype=np.float32)
        self.model = np.eye(4, dtype=np.float32)
        self.projection = np.eye(4, dtype=np.float32)
        
        self.timer = app.Timer('auto', connect=self.update, start=True)
        
        # Set uniforms (some are set later)
        self.program['u_model'] = self.model
        self.program['u_view'] = self.view
        
        # Set attributes
        self.program['a_position'] = np.zeros((N, 3), np.float32)
        self.program['a_offset'] = np.zeros((N, 1), np.float32)
        
        # Init
        self._timeout = 0
        self._active_block = 0
        for i in range(NBLOCKS):
            self._generate_stars()
        self._timeout = time.time() + SPEED