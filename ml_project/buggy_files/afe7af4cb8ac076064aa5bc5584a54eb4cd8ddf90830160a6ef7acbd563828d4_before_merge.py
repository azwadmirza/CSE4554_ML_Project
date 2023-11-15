    def __init__(
        self,
        data: pd.DataFrame,
        time_idx: str,
        target: Union[str, List[str]],
        group_ids: List[str],
        weight: Union[str, None] = None,
        max_encoder_length: int = 30,
        min_encoder_length: int = None,
        min_prediction_idx: int = None,
        min_prediction_length: int = None,
        max_prediction_length: int = 1,
        static_categoricals: List[str] = [],
        static_reals: List[str] = [],
        time_varying_known_categoricals: List[str] = [],
        time_varying_known_reals: List[str] = [],
        time_varying_unknown_categoricals: List[str] = [],
        time_varying_unknown_reals: List[str] = [],
        variable_groups: Dict[str, List[int]] = {},
        dropout_categoricals: List[str] = [],
        constant_fill_strategy={},
        allow_missings: bool = False,
        add_relative_time_idx: bool = False,
        add_target_scales: bool = False,
        add_encoder_length: Union[bool, str] = "auto",
        target_normalizer: Union[TorchNormalizer, NaNLabelEncoder, EncoderNormalizer, str] = "auto",
        categorical_encoders={},
        scalers={},
        randomize_length: Union[None, Tuple[float, float], bool] = False,
        predict_mode: bool = False,
    ):
        """
        Timeseries dataset holding data for models.

        The :ref:`tutorial on passing data to models <passing-data>` is helpful to understand the output of the dataset
        and how it is coupled to models.

        Each sample is a subsequence of a full time series. The subsequence consists of encoder and decoder/prediction
        timepoints for a given time series. This class constructs an index which defined which subsequences exists and
        can be samples from (``index`` attribute). The samples in the index are defined by by the various parameters.
        to the class (encoder and prediction lengths, minimum prediction length, randomize length and predict keywords).
        How samples are
        sampled into batches for training, is determined by the DataLoader. The class provides the
        :py:meth:`~TimeSeriesDataSet.to_dataloader` method to convert the dataset into a dataloader.

        Large datasets:

            Currently the class is limited to in-memory operations. If you have extremely large data,
            however, you can pass prefitted encoders and and scalers to it and a subset of sequences to the class to
            construct a valid dataset (plus, likely the EncoderNormalizer should be used to normalize targets).
            when fitting a network, you would then to create a custom DataLoader that rotates through the datasets.
            There is currently no in-built methods to do this.

        Args:
            data: dataframe with sequence data - each row can be identified with ``time_idx`` and the ``group_ids``
            time_idx: integer column denoting the time index. This columns is used to determine the sequence of samples.
                If there no missings observations, the time index should increase by ``+1`` for each subsequent sample.
                The first time_idx for each series does not necessarily have to be ``0`` but any value is allowed.
            target: column denoting the target or list of columns denoting the target - categorical or continous.
            group_ids: list of column names identifying a time series. This means that the ``group_ids`` identify
                a sample together with the ``time_idx``. If you have only one timeseries, set this to the
                name of column that is constant.
            weight: column name for weights. Defaults to None.
            max_encoder_length: maximum length to encode
            min_encoder_length: minimum allowed length to encode. Defaults to max_encoder_length.
            min_prediction_idx: minimum ``time_idx`` from where to start predictions. This parameter can be useful to
                create a validation or test set.
            max_prediction_length: maximum prediction/decoder length (choose this not too short as it can help
                convergence)
            min_prediction_length: minimum prediction/decoder length. Defaults to max_prediction_length
            static_categoricals: list of categorical variables that do not change over time,
                entries can be also lists which are then encoded together
                (e.g. useful for product categories)
            static_reals: list of continuous variables that do not change over time
            time_varying_known_categoricals: list of categorical variables that change over
                time and are know in the future, entries can be also lists which are then encoded together
                (e.g. useful for special days or promotion categories)
            time_varying_known_reals: list of continuous variables that change over
                time and are know in the future
            time_varying_unknown_categoricals: list of categorical variables that change over
                time and are not know in the future, entries can be also lists which are then encoded together
                (e.g. useful for weather categories)
            time_varying_unknown_reals: list of continuous variables that change over
                time and are not know in the future
            variable_groups: dictionary mapping a name to a list of columns in the data. The name should be present
                in a categorical or real class argument, to be able to encode or scale the columns by group.
            dropout_categoricals: list of categorical variables that are unknown when making a forecast without
                observed history
            constant_fill_strategy: dictionary of column names with constants to fill in missing values if there are
                gaps in the sequence (by default forward fill strategy is used). The values will be only used if
                ``allow_missings=True``. A common use case is to denote that demand was 0 if the sample is not in
                the dataset.
            allow_missings: if to allow missing timesteps that are automatically filled up. Missing values
                refer to gaps in the ``time_idx``, e.g. if a specific timeseries has only samples for
                1, 2, 4, 5, the sample for 3 will be generated on-the-fly.
                Allow missings does not deal with ``NA`` values. You should fill NA values before
                passing the dataframe to the TimeSeriesDataSet.
            add_relative_time_idx: if to add a relative time index as feature (i.e. for each sampled sequence, the index
                will range from -encoder_length to prediction_length)
            add_target_scales: if to add scales for target to static real features (i.e. add the center and scale
                of the unnormalized timeseries as features)
            add_encoder_length: if to add decoder length to list of static real variables. Defaults to "auto",
                i.e. yes if ``min_encoder_length != max_encoder_length``.
            target_normalizer: transformer that takes group_ids, target and time_idx to return normalized targets.
                You can choose from :py:class:`~TorchNormalizer`, :py:class:`~NaNLabelEncoder`,
                :py:class:`~EncoderNormalizer` or `None` for using not normalizer.
                By default an appropriate normalizer is chosen automatically.
            categorical_encoders: dictionary of scikit learn label transformers. If you have unobserved categories in
                the future, you can use the :py:class:`~pytorch_forecasting.encoders.NaNLabelEncoder` with
                ``add_nan=True``. Defaults effectively to sklearn's ``LabelEncoder()``. Prefittet encoders will not
                be fit again.
            scalers: dictionary of scikit learn scalers. Defaults to sklearn's ``StandardScaler()``.
                Other options are :py:class:`~pytorch_forecasting.data.encoders.EncoderNormalizer`,
                :py:class:`~pytorch_forecasting.data.encoders.GroupNormalizer` or scikit-learn's ``StandarScaler()``,
                ``RobustScaler()`` or `None` for using not normalizer.
                Prefittet encoders will not be fit again (with the exception of the
                :py:class:`~pytorch_forecasting.data.encoders.EncoderNormalizer`).
            randomize_length: None or False if not to randomize lengths. Tuple of beta distribution concentrations
                from which
                probabilities are sampled that are used to sample new sequence lengths with a binomial
                distribution.
                If True, defaults to (0.2, 0.05), i.e. ~1/4 of samples around minimum encoder length.
                Defaults to False otherwise.
            predict_mode: if to only iterate over each timeseries once (only the last provided samples).
                Effectively, this will take choose for each time series identified by ``group_ids``
                the last ``max_prediction_length`` samples of each time series as
                prediction samples and everthing previous up to ``max_encoder_length`` samples as encoder samples.
        """
        super().__init__()
        self.max_encoder_length = max_encoder_length
        assert isinstance(self.max_encoder_length, int), "max encoder length must be integer"
        if min_encoder_length is None:
            min_encoder_length = max_encoder_length
        self.min_encoder_length = min_encoder_length
        assert (
            self.min_encoder_length <= self.max_encoder_length
        ), "max encoder length has to be larger equals min encoder length"
        assert isinstance(self.min_encoder_length, int), "min encoder length must be integer"
        self.max_prediction_length = max_prediction_length
        assert isinstance(self.max_prediction_length, int), "max prediction length must be integer"
        if min_prediction_length is None:
            min_prediction_length = max_prediction_length
        self.min_prediction_length = min_prediction_length
        assert (
            self.min_prediction_length <= self.max_prediction_length
        ), "max prediction length has to be larger equals min prediction length"
        assert self.min_prediction_length > 0, "min prediction length must be larger than 0"
        assert isinstance(self.min_prediction_length, int), "min prediction length must be integer"
        self.target = target
        self.weight = weight
        self.time_idx = time_idx
        self.group_ids = [] + group_ids
        self.static_categoricals = [] + static_categoricals
        self.static_reals = [] + static_reals
        self.time_varying_known_categoricals = [] + time_varying_known_categoricals
        self.time_varying_known_reals = [] + time_varying_known_reals
        self.time_varying_unknown_categoricals = [] + time_varying_unknown_categoricals
        self.time_varying_unknown_reals = [] + time_varying_unknown_reals
        self.dropout_categoricals = [] + dropout_categoricals
        self.add_relative_time_idx = add_relative_time_idx

        # set automatic defaults
        if isinstance(randomize_length, bool):
            if not randomize_length:
                randomize_length = None
            else:
                randomize_length = (0.2, 0.05)
        self.randomize_length = randomize_length
        if min_prediction_idx is None:
            min_prediction_idx = data[self.time_idx].min()
        self.min_prediction_idx = min_prediction_idx
        self.constant_fill_strategy = {} if len(constant_fill_strategy) == 0 else constant_fill_strategy
        self.predict_mode = predict_mode
        self.allow_missings = allow_missings
        self.target_normalizer = target_normalizer
        self.categorical_encoders = {} if len(categorical_encoders) == 0 else categorical_encoders
        self.scalers = {} if len(scalers) == 0 else scalers
        self.add_target_scales = add_target_scales
        self.variable_groups = {} if len(variable_groups) == 0 else variable_groups

        # add_encoder_length
        if isinstance(add_encoder_length, str):
            assert (
                add_encoder_length == "auto"
            ), f"Only 'auto' allowed for add_encoder_length but found {add_encoder_length}"
            add_encoder_length = self.min_encoder_length != self.max_encoder_length
        assert isinstance(
            add_encoder_length, bool
        ), f"add_encoder_length should be boolean or 'auto' but found {add_encoder_length}"
        self.add_encoder_length = add_encoder_length

        # target normalizer
        self._set_target_normalizer(data)

        # overwrite values
        self.reset_overwrite_values()

        for target in self.target_names:
            assert (
                target not in self.time_varying_known_reals
            ), f"target {target} should be an unknown continuous variable in the future"

        # set data
        assert data.index.is_unique, "data index has to be unique"
        if min_prediction_idx is not None:
            data = data[lambda x: data[self.time_idx] >= self.min_prediction_idx - self.max_encoder_length]
        data = data.sort_values(self.group_ids + [self.time_idx])

        # add time index relative to prediction position
        if self.add_relative_time_idx:
            assert (
                "relative_time_idx" not in data.columns
            ), "relative_time_idx is a protected column and must not be present in data"
            if "relative_time_idx" not in self.time_varying_known_reals and "relative_time_idx" not in self.reals:
                self.time_varying_known_reals.append("relative_time_idx")
            data["relative_time_idx"] = 0.0  # dummy - real value will be set dynamiclly in __getitem__()

        # add decoder length to static real variables
        if self.add_encoder_length:
            assert (
                "encoder_length" not in data.columns
            ), "encoder_length is a protected column and must not be present in data"
            if "encoder_length" not in self.time_varying_known_reals and "encoder_length" not in self.reals:
                self.static_reals.append("encoder_length")
            data["encoder_length"] = 0  # dummy - real value will be set dynamiclly in __getitem__()

        # validate
        self._validate_data(data)

        # preprocess data
        data = self._preprocess_data(data)

        # create index
        self.index = self._construct_index(data, predict_mode=predict_mode)

        # convert to torch tensor for high performance data loading later
        self.data = self._data_to_tensors(data)