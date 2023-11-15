    def __init__(
        self,
        metrics_separator: str = " - ",
        overall_bar_format: str = "{l_bar}{bar} {n_fmt}/{total_fmt} ETA: "
        "{remaining}s,  {rate_fmt}{postfix}",
        epoch_bar_format: str = "{n_fmt}/{total_fmt}{bar} ETA: "
        "{remaining}s - {desc}",
        metrics_format: str = "{name}: {value:0.4f}",
        update_per_second: int = 10,
        leave_epoch_progress: bool = True,
        leave_overall_progress: bool = True,
        show_epoch_progress: bool = True,
        show_overall_progress: bool = True,
    ):

        try:
            # import tqdm here because tqdm is not a required package
            # for addons
            import tqdm

            version_message = "Please update your TQDM version to >= 4.36.1, "
            "you have version {}. To update, run !pip install -U tqdm"
            assert tqdm.__version__ >= "4.36.1", version_message.format(
                tqdm.__version__
            )
            from tqdm.auto import tqdm

            self.tqdm = tqdm
        except ImportError:
            raise ImportError("Please install tqdm via pip install tqdm")

        self.metrics_separator = metrics_separator
        self.overall_bar_format = overall_bar_format
        self.epoch_bar_format = epoch_bar_format
        self.leave_epoch_progress = leave_epoch_progress
        self.leave_overall_progress = leave_overall_progress
        self.show_epoch_progress = show_epoch_progress
        self.show_overall_progress = show_overall_progress
        self.metrics_format = metrics_format

        # compute update interval (inverse of update per second)
        self.update_interval = 1 / update_per_second

        self.last_update_time = time.time()
        self.overall_progress_tqdm = None
        self.epoch_progress_tqdm = None
        self.num_epochs = None
        self.logs = None
        self.metrics = None