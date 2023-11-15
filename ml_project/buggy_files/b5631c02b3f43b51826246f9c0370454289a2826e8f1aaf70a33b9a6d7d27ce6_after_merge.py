    def __init__(self, filepath, monitor='val_loss', verbose=0,
                 save_top_k=1, save_weights_only=False,
                 mode='auto', period=1, prefix=''):
        super(ModelCheckpoint, self).__init__()
        if (
            save_top_k and
            os.path.isdir(filepath) and
            len(os.listdir(filepath)) > 0
        ):
            warnings.warn(
                f"Checkpoint directory {filepath} exists and is not empty with save_top_k != 0."
                "All files in this directory will be deleted when a checkpoint is saved!"
            )

        self.monitor = monitor
        self.verbose = verbose
        self.filepath = filepath
        os.makedirs(filepath, exist_ok=True)
        self.save_top_k = save_top_k
        self.save_weights_only = save_weights_only
        self.period = period
        self.epochs_since_last_check = 0
        self.prefix = prefix
        self.best_k_models = {}
        # {filename: monitor}
        self.kth_best_model = ''
        self.best = 0

        if mode not in ['auto', 'min', 'max']:
            warnings.warn(
                f'ModelCheckpoint mode {mode} is unknown, '
                'fallback to auto mode.', RuntimeWarning)
            mode = 'auto'

        if mode == 'min':
            self.monitor_op = np.less
            self.kth_value = np.Inf
            self.mode = 'min'
        elif mode == 'max':
            self.monitor_op = np.greater
            self.kth_value = -np.Inf
            self.mode = 'max'
        else:
            if 'acc' in self.monitor or self.monitor.startswith('fmeasure'):
                self.monitor_op = np.greater
                self.kth_value = -np.Inf
                self.mode = 'max'
            else:
                self.monitor_op = np.less
                self.kth_value = np.Inf
                self.mode = 'min'