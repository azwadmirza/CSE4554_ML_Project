def fetch_openml(name=None, version='active', data_id=None, data_home=None,
                 target_column='default-target', cache=True, return_X_y=False,
                 as_frame=False):
    """Fetch dataset from openml by name or dataset id.

    Datasets are uniquely identified by either an integer ID or by a
    combination of name and version (i.e. there might be multiple
    versions of the 'iris' dataset). Please give either name or data_id
    (not both). In case a name is given, a version can also be
    provided.

    Read more in the :ref:`User Guide <openml>`.

    .. note:: EXPERIMENTAL

        The API is experimental (particularly the return value structure),
        and might have small backward-incompatible changes in future releases.

    Parameters
    ----------
    name : str or None
        String identifier of the dataset. Note that OpenML can have multiple
        datasets with the same name.

    version : integer or 'active', default='active'
        Version of the dataset. Can only be provided if also ``name`` is given.
        If 'active' the oldest version that's still active is used. Since
        there may be more than one active version of a dataset, and those
        versions may fundamentally be different from one another, setting an
        exact version is highly recommended.

    data_id : int or None
        OpenML ID of the dataset. The most specific way of retrieving a
        dataset. If data_id is not given, name (and potential version) are
        used to obtain a dataset.

    data_home : string or None, default None
        Specify another download and cache folder for the data sets. By default
        all scikit-learn data is stored in '~/scikit_learn_data' subfolders.

    target_column : string, list or None, default 'default-target'
        Specify the column name in the data to use as target. If
        'default-target', the standard target column a stored on the server
        is used. If ``None``, all columns are returned as data and the
        target is ``None``. If list (of strings), all columns with these names
        are returned as multi-target (Note: not all scikit-learn classifiers
        can handle all types of multi-output combinations)

    cache : boolean, default=True
        Whether to cache downloaded datasets using joblib.

    return_X_y : boolean, default=False.
        If True, returns ``(data, target)`` instead of a Bunch object. See
        below for more information about the `data` and `target` objects.

    as_frame : boolean, default=False
        If True, the data is a pandas DataFrame including columns with
        appropriate dtypes (numeric, string or categorical). The target is
        a pandas DataFrame or Series depending on the number of target_columns.
        The Bunch will contain a ``frame`` attribute with the target and the
        data. If ``return_X_y`` is True, then ``(data, target)`` will be pandas
        DataFrames or Series as describe above.

    Returns
    -------

    data : Bunch
        Dictionary-like object, with attributes:

        data : np.array, scipy.sparse.csr_matrix of floats, or pandas DataFrame
            The feature matrix. Categorical features are encoded as ordinals.
        target : np.array, pandas Series or DataFrame
            The regression target or classification labels, if applicable.
            Dtype is float if numeric, and object if categorical. If
            ``as_frame`` is True, ``target`` is a pandas object.
        DESCR : str
            The full description of the dataset
        feature_names : list
            The names of the dataset columns
        categories : dict or None
            Maps each categorical feature name to a list of values, such
            that the value encoded as i is ith in the list. If ``as_frame``
            is True, this is None.
        details : dict
            More metadata from OpenML
        frame : pandas DataFrame
            Only present when `as_frame=True`. DataFrame with ``data`` and
            ``target``.

    (data, target) : tuple if ``return_X_y`` is True

        .. note:: EXPERIMENTAL

            This interface is **experimental** and subsequent releases may
            change attributes without notice (although there should only be
            minor changes to ``data`` and ``target``).

        Missing values in the 'data' are represented as NaN's. Missing values
        in 'target' are represented as NaN's (numerical target) or None
        (categorical target)
    """
    data_home = get_data_home(data_home=data_home)
    data_home = join(data_home, 'openml')
    if cache is False:
        # no caching will be applied
        data_home = None

    # check valid function arguments. data_id XOR (name, version) should be
    # provided
    if name is not None:
        # OpenML is case-insensitive, but the caching mechanism is not
        # convert all data names (str) to lower case
        name = name.lower()
        if data_id is not None:
            raise ValueError(
                "Dataset data_id={} and name={} passed, but you can only "
                "specify a numeric data_id or a name, not "
                "both.".format(data_id, name))
        data_info = _get_data_info_by_name(name, version, data_home)
        data_id = data_info['did']
    elif data_id is not None:
        # from the previous if statement, it is given that name is None
        if version != "active":
            raise ValueError(
                "Dataset data_id={} and version={} passed, but you can only "
                "specify a numeric data_id or a version, not "
                "both.".format(data_id, name))
    else:
        raise ValueError(
            "Neither name nor data_id are provided. Please provide name or "
            "data_id.")

    data_description = _get_data_description_by_id(data_id, data_home)
    if data_description['status'] != "active":
        warn("Version {} of dataset {} is inactive, meaning that issues have "
             "been found in the dataset. Try using a newer version from "
             "this URL: {}".format(
                data_description['version'],
                data_description['name'],
                data_description['url']))
    if 'error' in data_description:
        warn("OpenML registered a problem with the dataset. It might be "
             "unusable. Error: {}".format(data_description['error']))
    if 'warning' in data_description:
        warn("OpenML raised a warning on the dataset. It might be "
             "unusable. Warning: {}".format(data_description['warning']))

    return_sparse = False
    if data_description['format'].lower() == 'sparse_arff':
        return_sparse = True

    if as_frame and return_sparse:
        raise ValueError('Cannot return dataframe with sparse data')

    # download data features, meta-info about column types
    features_list = _get_data_features(data_id, data_home)

    if not as_frame:
        for feature in features_list:
            if 'true' in (feature['is_ignore'], feature['is_row_identifier']):
                continue
            if feature['data_type'] == 'string':
                raise ValueError('STRING attributes are not supported for '
                                 'array representation. Try as_frame=True')

    if target_column == "default-target":
        # determines the default target based on the data feature results
        # (which is currently more reliable than the data description;
        # see issue: https://github.com/openml/OpenML/issues/768)
        target_columns = [feature['name'] for feature in features_list
                          if feature['is_target'] == 'true']
    elif isinstance(target_column, str):
        # for code-simplicity, make target_column by default a list
        target_columns = [target_column]
    elif target_column is None:
        target_columns = []
    elif isinstance(target_column, list):
        target_columns = target_column
    else:
        raise TypeError("Did not recognize type of target_column"
                        "Should be str, list or None. Got: "
                        "{}".format(type(target_column)))
    data_columns = _valid_data_column_names(features_list,
                                            target_columns)

    # prepare which columns and data types should be returned for the X and y
    features_dict = {feature['name']: feature for feature in features_list}

    # XXX: col_slice_y should be all nominal or all numeric
    _verify_target_data_type(features_dict, target_columns)

    col_slice_y = [int(features_dict[col_name]['index'])
                   for col_name in target_columns]

    col_slice_x = [int(features_dict[col_name]['index'])
                   for col_name in data_columns]
    for col_idx in col_slice_y:
        feat = features_list[col_idx]
        nr_missing = int(feat['number_of_missing_values'])
        if nr_missing > 0:
            raise ValueError('Target column {} has {} missing values. '
                             'Missing values are not supported for target '
                             'columns. '.format(feat['name'], nr_missing))

    # determine arff encoding to return
    if not return_sparse:
        data_qualities = _get_data_qualities(data_id, data_home)
        shape = _get_data_shape(data_qualities)
        # if the data qualities were not available, we can still get the
        # n_features from the feature list, with the n_samples unknown
        if shape is None:
            shape = (-1, len(features_list))
    else:
        shape = None

    # obtain the data
    arff = _download_data_arff(data_description['file_id'], return_sparse,
                               data_home, encode_nominal=not as_frame)

    description = "{}\n\nDownloaded from openml.org.".format(
        data_description.pop('description'))

    nominal_attributes = None
    frame = None
    if as_frame:
        columns = data_columns + target_columns
        frame = _convert_arff_data_dataframe(arff, columns, features_dict)
        X = frame[data_columns]
        if len(target_columns) >= 2:
            y = frame[target_columns]
        elif len(target_columns) == 1:
            y = frame[target_columns[0]]
        else:
            y = None
    else:
        # nominal attributes is a dict mapping from the attribute name to the
        # possible values. Includes also the target column (which will be
        # popped off below, before it will be packed in the Bunch object)
        nominal_attributes = {k: v for k, v in arff['attributes']
                              if isinstance(v, list) and
                              k in data_columns + target_columns}

        X, y = _convert_arff_data(arff['data'], col_slice_x,
                                  col_slice_y, shape)

        is_classification = {col_name in nominal_attributes
                             for col_name in target_columns}
        if not is_classification:
            # No target
            pass
        elif all(is_classification):
            y = np.hstack([
                np.take(
                    np.asarray(nominal_attributes.pop(col_name), dtype='O'),
                    y[:, i:i + 1].astype(int, copy=False))
                for i, col_name in enumerate(target_columns)
            ])
        elif any(is_classification):
            raise ValueError('Mix of nominal and non-nominal targets is not '
                             'currently supported')

        # reshape y back to 1-D array, if there is only 1 target column; back
        # to None if there are not target columns
        if y.shape[1] == 1:
            y = y.reshape((-1,))
        elif y.shape[1] == 0:
            y = None

    if return_X_y:
        return X, y

    bunch = Bunch(
        data=X, target=y, frame=frame, feature_names=data_columns,
        DESCR=description, details=data_description,
        categories=nominal_attributes,
        url="https://www.openml.org/d/{}".format(data_id))

    return bunch