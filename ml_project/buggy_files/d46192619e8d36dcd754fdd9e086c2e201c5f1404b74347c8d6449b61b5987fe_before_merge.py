    def fit(self, x, y, x_test=None, y_test=None, time_limit=None):
        x = np.array(x)
        y = np.array(y).flatten()
        validate_xy(x, y)
        y = self.transform_y(y)
        if x_test is None or y_test is None:
            # Divide training data into training and testing data.
            validation_set_size = int(len(y) * Constant.VALIDATION_SET_SIZE)
            validation_set_size = min(validation_set_size, 500)
            validation_set_size = max(validation_set_size, 1)
            x_train, x_test, y_train, y_test = train_test_split(x, y,
                                                                test_size=validation_set_size,
                                                                random_state=42)
        else:
            x_train = x
            y_train = y
        # Transform x_train
        if self.data_transformer is None:
            self.data_transformer = ImageDataTransformer(x, augment=self.augment)

        # Wrap the data into DataLoaders
        train_data = self.data_transformer.transform_train(x_train, y_train)
        test_data = self.data_transformer.transform_test(x_test, y_test)

        # Save the classifier
        pickle_to_file(self, os.path.join(self.path, 'classifier'))

        if time_limit is None:
            time_limit = 24 * 60 * 60

        self.cnn.fit(self.get_n_output_node(), x_train.shape, train_data, test_data, time_limit)