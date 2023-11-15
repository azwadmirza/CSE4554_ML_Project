    def __init__(self, verbose=False, path=None, resume=False, searcher_args=None, augment=None):
        """Initialize the instance.

        The classifier will be loaded from the files in 'path' if parameter 'resume' is True.
        Otherwise it would create a new one.

        Args:
            verbose: A boolean of whether the search process will be printed to stdout.
            path: A string. The path to a directory, where the intermediate results are saved.
            resume: A boolean. If True, the classifier will continue to previous work saved in path.
                Otherwise, the classifier will start a new search.
            augment: A boolean value indicating whether the data needs augmentation. If not define, then it
                will use the value of Constant.DATA_AUGMENTATION which is True by default.

        """
        super().__init__(verbose)

        if searcher_args is None:
            searcher_args = {}

        if path is None:
            path = temp_folder_generator()

        if augment is None:
            augment = Constant.DATA_AUGMENTATION

        self.path = path
        if has_file(os.path.join(self.path, 'classifier')) and resume:
            classifier = pickle_from_file(os.path.join(self.path, 'classifier'))
            self.__dict__ = classifier.__dict__
        else:
            self.y_encoder = None
            self.data_transformer = None
            self.verbose = verbose
            self.augment = augment
            self.cnn = CnnModule(self.loss, self.metric, searcher_args, path, verbose)