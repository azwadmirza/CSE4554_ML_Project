    def __init__(self, trainer):

        self.enabled = 'PL_DEV_DEBUG' in os.environ
        self.trainer = trainer
        self.logged_metrics = []
        self.pbar_added_metrics = []
        self.saved_losses = []
        self.saved_val_losses = []
        self.saved_test_losses = []
        self.early_stopping_history = []
        self.checkpoint_callback_history = []