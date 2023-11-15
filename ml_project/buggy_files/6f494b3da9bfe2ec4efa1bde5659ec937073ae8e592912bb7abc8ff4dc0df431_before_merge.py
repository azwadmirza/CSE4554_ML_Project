def preprocess_for_prediction(
        model_path,
        split,
        dataset_type='generic',
        data_csv=None,
        data_hdf5=None,
        train_set_metadata=None,
        only_predictions=False
):
    """Preprocesses the dataset to parse it into a format that is usable by the
    Ludwig core
        :param model_path: The input data that is joined with the model
               hyperparameter file to create the model definition file
        :type model_path: Str
        :param dataset_type: Generic
        :type: Str
        :param split: Splits the data into the train and test sets
        :param data_csv: The CSV input data file
        :param data_hdf5: The hdf5 data file if there is no csv data file
        :param train_set_metadata: Train set metadata for the input features
        :param only_predictions: If False does not load output features
        :returns: Dataset, Train set metadata
        """
    model_definition = load_json(
        os.path.join(model_path, MODEL_HYPERPARAMETERS_FILE_NAME)
    )
    preprocessing_params = merge_dict(
        default_preprocessing_parameters,
        model_definition['preprocessing']
    )

    # Check if hdf5 and json already exist
    if data_csv is not None:
        data_hdf5_fp = os.path.splitext(data_csv)[0] + '.hdf5'
        if os.path.isfile(data_hdf5_fp):
            logging.info(
                'Found hdf5 with the same filename of the csv, using it instead'
            )
            data_csv = None
            data_hdf5 = data_hdf5_fp

    # Load data
    _, _, build_dataset, _ = get_dataset_fun(dataset_type)
    train_set_metadata = load_metadata(train_set_metadata)
    features = (model_definition['input_features'] +
                ([] if only_predictions
                 else model_definition['output_features']))
    if split == 'full':
        if data_hdf5 is not None:
            dataset = load_data(
                data_hdf5,
                model_definition['input_features'],
                [] if only_predictions else model_definition['output_features'],
                split_data=False, shuffle_training=False
            )
        else:
            dataset, train_set_metadata = build_dataset(
                data_csv,
                features,
                preprocessing_params,
                train_set_metadata=train_set_metadata
            )
    else:
        if data_hdf5 is not None:
            training, test, validation = load_data(
                data_hdf5,
                model_definition['input_features'],
                [] if only_predictions else model_definition['output_features'],
                shuffle_training=False
            )

            if split == 'training':
                dataset = training
            elif split == 'validation':
                dataset = validation
            else:  # if split == 'test':
                dataset = test
        else:
            dataset, train_set_metadata = build_dataset(
                data_csv,
                features,
                preprocessing_params,
                train_set_metadata=train_set_metadata
            )

    replace_text_feature_level(
        model_definition['input_features'] +
        ([] if only_predictions else model_definition['output_features']),
        [dataset]
    )

    dataset = Dataset(
        dataset,
        model_definition['input_features'],
        [] if only_predictions else model_definition['output_features'],
        data_hdf5,
    )

    return dataset, train_set_metadata