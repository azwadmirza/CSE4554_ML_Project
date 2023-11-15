    def train_online(
            self,
            data_df=None,
            data_csv=None,
            data_dict=None,
            batch_size=None,
            learning_rate=None,
            regularization_lambda=None,
            dropout_rate=None,
            bucketing_field=None,
            gpus=None,
            gpu_fraction=1,
            logging_level=logging.ERROR,
    ):
        """This function is used to perform one epoch of training of the model 
        on the specified dataset.

        # Inputs

        :param data_df: (DataFrame) dataframe containing data.
        :param data_csv: (string) input data CSV file.
        :param data_dict: (dict) input data dictionary. It is expected to 
               contain one key for each field and the values have to be lists of 
               the same length. Each index in the lists corresponds to one 
               datapoint. For example a data set consisting of two datapoints 
               with a text and a class may be provided as the following dict 
               ``{'text_field_name': ['text of the first datapoint', text of the
               second datapoint'], 'class_filed_name': ['class_datapoints_1', 
               'class_datapoints_2']}`.
        :param batch_size: (int) the batch size to use for training. By default 
               it's the one specified in the model definition.
        :param learning_rate: (float) the learning rate to use for training. By
               default the values is the one specified in the model definition.
        :param regularization_lambda: (float) the regularization lambda
               parameter to use for training. By default the values is the one
               specified in the model definition.
        :param dropout_rate: (float) the dropout rate to use for training. By
               default the values is the one specified in the model definition.
        :param bucketing_field: (string) the bucketing field to use for
               bucketing the data. By default the values is one specified in the
               model definition.
        :param gpus: (string, default: `None`) list of GPUs to use (it uses the
               same syntax of CUDA_VISIBLE_DEVICES)
        :param gpu_fraction: (float, default `1.0`) fraction of GPU memory to
               initialize the process with
        :param logging_level: (int, default: `logging.ERROR`) logging level to
               use for logging. Use logging constants like `logging.DEBUG`,
               `logging.INFO` and `logging.ERROR`. By default only errors will
               be printed.

        There are three ways to provide data: by dataframes using the `data_df`
        parameter, by CSV using the `data_csv` parameter and by dictionary,
        using the `data_dict` parameter.

        The DataFrame approach uses data previously obtained and put in a
        dataframe, the CSV approach loads data from a CSV file, while dict
        approach uses data organized by keys representing columns and values
        that are lists of the datapoints for each. For example a data set
        consisting of two datapoints with a text and a class may be provided as
        the following dict ``{'text_field_name}: ['text of the first datapoint',
        text of the second datapoint'], 'class_filed_name':
        ['class_datapoints_1', 'class_datapoints_2']}`.
        """
        logging.getLogger().setLevel(logging_level)
        if logging_level in {logging.WARNING, logging.ERROR, logging.CRITICAL}:
            set_disable_progressbar(True)

        if (self.model is None or self.model_definition is None
                or self.train_set_metadata is None):
            raise ValueError('Model has not been initialized or loaded')

        if data_df is None:
            data_df = self._read_data(data_csv, data_dict)
            data_df.csv = data_csv

        if batch_size is None:
            batch_size = self.model_definition['training']['batch_size']
        if learning_rate is None:
            learning_rate = self.model_definition['training']['learning_rate']
        if regularization_lambda is None:
            regularization_lambda = self.model_definition['training'][
                'regularization_lambda'
            ]
        if dropout_rate is None:
            dropout_rate = self.model_definition['training']['dropout_rate'],
        if bucketing_field is None:
            bucketing_field = self.model_definition['training'][
                'bucketing_field'
            ]

        logging.debug('Preprocessing {} datapoints'.format(len(data_df)))
        features_to_load = (self.model_definition['input_features'] +
                            self.model_definition['output_features'])
        preprocessed_data = build_data(
            data_df,
            features_to_load,
            self.train_set_metadata,
            self.model_definition['preprocessing']
        )
        replace_text_feature_level(
            self.model_definition['input_features'] +
            self.model_definition['output_features'],
            [preprocessed_data]
        )
        dataset = Dataset(
            preprocessed_data,
            self.model_definition['input_features'],
            self.model_definition['output_features'],
            None
        )

        logging.debug('Training batch')
        self.model.train_online(
            dataset,
            batch_size=batch_size,
            learning_rate=learning_rate,
            regularization_lambda=regularization_lambda,
            dropout_rate=dropout_rate,
            bucketing_field=bucketing_field,
            gpus=gpus,
            gpu_fraction=gpu_fraction)