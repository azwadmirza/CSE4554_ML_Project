    def add_feature_data(
            feature,
            dataset_df,
            data,
            metadata,
            preprocessing_parameters
    ):
        set_default_value(
            feature,
            'in_memory',
            preprocessing_parameters['in_memory']
        )

        if ('height' in preprocessing_parameters or
                'width' in preprocessing_parameters):
            should_resize = True
            try:
                provided_height = int(preprocessing_parameters[HEIGHT])
                provided_width = int(preprocessing_parameters[WIDTH])
            except ValueError as e:
                raise ValueError(
                    'Image height and width must be set and have '
                    'positive integer values: ' + str(e)
                )
            if (provided_height <= 0 or provided_width <= 0):
                raise ValueError(
                    'Image height and width must be positive integers'
                )
        else:
            should_resize = False

        csv_path = None
        if hasattr(dataset_df, 'csv'):
            csv_path = os.path.dirname(os.path.abspath(dataset_df.csv))

        num_images = len(dataset_df)

        height = 0
        width = 0
        num_channels = 1

        if num_images > 0:
            # here if a width and height have not been specified
            # we assume that all images have the same wifth and im_height
            # thus the width and height of the first one are the same
            # of all the other ones
            if (csv_path is None and
                    not os.path.isabs(dataset_df[feature['name']][0])):
                raise ValueError(
                    'Image file paths must be absolute'
                )

            first_image = imread(
                get_abs_path(
                    csv_path,
                    dataset_df[feature['name']][0]
                )
            )

            height = first_image.shape[0]
            width = first_image.shape[1]

            if first_image.ndim == 2:
                num_channels = 1
            else:
                num_channels = first_image.shape[2]

        if should_resize:
            height = provided_height
            width = provided_width

        metadata[feature['name']]['preprocessing']['height'] = height
        metadata[feature['name']]['preprocessing']['width'] = width
        metadata[feature['name']]['preprocessing'][
            'num_channels'] = num_channels

        if feature['in_memory']:
            data[feature['name']] = np.empty(
                (num_images, height, width, num_channels),
                dtype=np.int8
            )
            for i in range(len(dataset_df)):
                img = imread(
                    get_abs_path(
                        csv_path,
                        dataset_df[feature['name']][i]
                    )
                )
                if img.ndim == 2:
                    img = img.reshape((img.shape[0], img.shape[1], 1))
                if should_resize:
                    img = resize_image(
                        img,
                        (height, width),
                        preprocessing_parameters['resize_method']
                    )
                data[feature['name']][i, :, :, :] = img
        else:
            data_fp = os.path.splitext(dataset_df.csv)[0] + '.hdf5'
            mode = 'w'
            if os.path.isfile(data_fp):
                mode = 'r+'
            with h5py.File(data_fp, mode) as h5_file:
                image_dataset = h5_file.create_dataset(
                    feature['name'] + '_data',
                    (num_images, height, width, num_channels),
                    dtype=np.uint8
                )
                for i in range(len(dataset_df)):
                    img = imread(
                        get_abs_path(
                            csv_path,
                            dataset_df[feature['name']][i]
                        )
                    )
                    if img.ndim == 2:
                        img = img.reshape((img.shape[0], img.shape[1], 1))
                    if should_resize:
                        img = resize_image(
                            img,
                            (height, width),
                            preprocessing_parameters['resize_method'],
                        )

                    image_dataset[i, :height, :width, :] = img

            data[feature['name']] = np.arange(num_images)