    def fit_before_convert(self, dataset):
        # If in tf.data.Dataset, must be encoded already.
        if isinstance(dataset, tf.data.Dataset):
            if not self.num_classes:
                shape = utils.dataset_shape(dataset)[0]
                # Single column with 0s and 1s.
                if shape == 1:
                    self.num_classes = 2
                else:
                    self.num_classes = shape
            return
        if isinstance(dataset, pd.DataFrame):
            dataset = dataset.values
        if isinstance(dataset, pd.Series):
            dataset = dataset.values.reshape(-1, 1)
        # Not label.
        if len(dataset.flatten()) != len(dataset):
            self.num_classes = dataset.shape[1]
            return
        labels = set(dataset.flatten())
        if self.num_classes is None:
            self.num_classes = len(labels)
        if self.num_classes == 2:
            self.label_encoder = encoders.LabelEncoder()
        elif self.num_classes > 2:
            self.label_encoder = encoders.OneHotEncoder()
        elif self.num_classes < 2:
            raise ValueError('Expect the target data for {name} to have '
                             'at least 2 classes, but got {num_classes}.'
                             .format(name=self.name, num_classes=self.num_classes))
        self.label_encoder.fit(dataset)