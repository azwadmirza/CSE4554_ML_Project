    def __init__(
        self,
        tokenizer,
        max_seq_len,
        label_list,
        metrics,
        train_filename,
        dev_filename,
        test_filename,
        dev_split,
        data_dir,
        label_dtype=torch.long,
        multiprocessing_chunk_size=1_000,
        max_processes=128,
        share_all_baskets_for_multiprocessing=False,
    ):
        """
        Initialize a generic Processor

        :param tokenizer: Used to split a sentence (str) into tokens.
        :param max_seq_len: Samples are truncated after this many tokens.
        :type max_seq_len: int
        :param label_list: List of all unique target labels.
        :type label_list: list
        :param metrics: The metric used for evaluation, one per prediction head.
                        Choose from mcc, acc, acc_f1, pear_spear, seq_f1, f1_macro, squad.
        :type metrics: list or str
        :param train_filename: The name of the file containing training data.
        :type train_filename: str
        :param dev_filename: The name of the file containing the dev data. If None and 0.0 < dev_split < 1.0 the dev set
                             will be a slice of the train set.
        :type dev_filename: str or None
        :param test_filename: The name of the file containing test data.
        :type test_filename: str
        :param dev_split: The proportion of the train set that will sliced. Only works if dev_filename is set to None
        :type dev_split: float
        :param data_dir: The directory in which the train, test and perhaps dev files can be found.
        :type data_dir: str
        :param label_dtype: The torch dtype for the labels.
        :param max_processes: maximum number of processing to use for Multiprocessing.
        :type max_processes: int
        """

        # The Multiprocessing functions in the Class are classmethods to avoid passing(and pickling) of class-objects
        # that are very large in size(eg, self.baskets). Since classmethods have access to only class attributes, all
        # objects required in Multiprocessing must be set as class attributes.
        Processor.tokenizer = tokenizer
        Processor.max_seq_len = max_seq_len
        Processor.label_list = label_list

        # data sets
        self.train_filename = train_filename
        self.dev_filename = dev_filename
        self.test_filename = test_filename
        self.dev_split = dev_split
        self.data_dir = data_dir
        # labels
        self.label_dtype = label_dtype
        self.label_maps = []
        # multiprocessing
        self.multiprocessing_chunk_size = multiprocessing_chunk_size
        self.share_all_baskets_for_multiprocessing = (
            share_all_baskets_for_multiprocessing
        )
        self.max_processes = max_processes
        # others
        self.metrics = [metrics] if isinstance(metrics, str) else metrics

        # create label maps (one per prediction head)
        if any(isinstance(i, list) for i in label_list):
            for labels_per_head in label_list:
                map = {i: label for i, label in enumerate(labels_per_head)}
                self.label_maps.append(map)
        else:
            map = {i: label for i, label in enumerate(label_list)}
            self.label_maps.append(map)

        self.baskets = []

        self._log_params()