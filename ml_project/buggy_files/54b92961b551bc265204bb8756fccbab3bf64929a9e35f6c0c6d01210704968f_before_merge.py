    def __init__(self, off_screen=False, notebook=None):
        """
        Initialize a vtk plotting object
        """
        log.debug('Initializing')
        def onTimer(iren, eventId):
            if 'TimerEvent' == eventId:
                # TODO: python binding didn't provide
                # third parameter, which indicate right timer id
                # timer_id = iren.GetCommand(44)
                # if timer_id != self.right_timer_id:
                #     return
                self.iren.TerminateApp()

        self._labels = []

        if notebook is None:
            notebook = type(get_ipython()).__module__.startswith('ipykernel.')
        self.notebook = notebook
        if self.notebook:
            off_screen = True
        self.off_screen = off_screen

        # initialize render window
        self.renderer = vtk.vtkRenderer()
        self.ren_win = vtk.vtkRenderWindow()
        self.ren_win.AddRenderer(self.renderer)

        if self.off_screen:
            self.ren_win.SetOffScreenRendering(1)
        else:  # Allow user to interact
            self.iren = vtk.vtkRenderWindowInteractor()
            self.iren.SetDesiredUpdateRate(30.0)
            self.iren.SetRenderWindow(self.ren_win)
            istyle = vtk.vtkInteractorStyleTrackballCamera()
            self.iren.SetInteractorStyle(istyle)
            self.iren.AddObserver("KeyPressEvent", self.key_press_event)

        # Set background
        self.set_background(DEFAULT_BACKGROUND)

        # initialize image filter
        self.ifilter = vtk.vtkWindowToImageFilter()
        self.ifilter.SetInput(self.ren_win)
        self.ifilter.SetInputBufferTypeToRGB()
        self.ifilter.ReadFrontBufferOff()

        # add timer event if interactive render exists
        if hasattr(self, 'iren'):
            self.iren.AddObserver(vtk.vtkCommand.TimerEvent, onTimer)

        # track if the camera has been setup
        self.camera_set = False
        self.first_time = True
        self.bounds = [0,1, 0,1, 0,1]