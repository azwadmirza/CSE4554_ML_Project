    def __init__(self, kernel_manager, **kwargs):
        super(KernelSessionManager, self).__init__(**kwargs)
        self.kernel_manager = kernel_manager
        self._sessions = dict()
        self.kernel_session_file = os.path.join(self.get_sessions_loc(), 'kernels.json')
        self._load_sessions()