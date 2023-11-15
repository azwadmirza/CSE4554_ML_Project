    def _fit(self, X_train, y_train, X_val=None, y_val=None, time_limit=None, reporter=None, **kwargs):
        """ X_train (pd.DataFrame): training data features (not necessarily preprocessed yet)
            X_val (pd.DataFrame): test data features (should have same column names as Xtrain)
            y_train (pd.Series):
            y_val (pd.Series): are pandas Series
            kwargs: Can specify amount of compute resources to utilize (num_cpus, num_gpus).
        """
        start_time = time.time()
        params = self.params.copy()
        self.verbosity = kwargs.get('verbosity', 2)
        params = fixedvals_from_searchspaces(params)
        if self.feature_metadata is None:
            raise ValueError("Trainer class must set feature_metadata for this model")
        # print('features: ', self.features)
        if 'num_cpus' in kwargs:
            self.num_dataloading_workers = max(1, int(kwargs['num_cpus']/2.0))
        else:
            self.num_dataloading_workers = 1
        if self.num_dataloading_workers == 1:
            self.num_dataloading_workers = 0  # 0 is always faster and uses less memory than 1
        self.batch_size = params['batch_size']
        train_dataset, val_dataset = self.generate_datasets(X_train=X_train, y_train=y_train, params=params, X_val=X_val, y_val=y_val)
        logger.log(15, "Training data for neural network has: %d examples, %d features (%d vector, %d embedding, %d language)" %
              (train_dataset.num_examples, train_dataset.num_features,
               len(train_dataset.feature_groups['vector']), len(train_dataset.feature_groups['embed']),
               len(train_dataset.feature_groups['language']) ))
        # self._save_preprocessor() # TODO: should save these things for hyperparam tunning. Need one HP tuner for network-specific HPs, another for preprocessing HPs.

        if 'num_gpus' in kwargs and kwargs['num_gpus'] >= 1:  # Currently cannot use >1 GPU
            self.ctx = mx.gpu()  # Currently cannot use more than 1 GPU
        else:
            self.ctx = mx.cpu()
        self.get_net(train_dataset, params=params)

        if time_limit:
            time_elapsed = time.time() - start_time
            time_limit = time_limit - time_elapsed

        self.train_net(train_dataset=train_dataset, params=params, val_dataset=val_dataset, initialize=True, setup_trainer=True, time_limit=time_limit, reporter=reporter)
        self.params_post_fit = params
        """
        # TODO: if we don't want to save intermediate network parameters, need to do something like saving in temp directory to clean up after training:
        with make_temp_directory() as temp_dir:
            save_callback = SaveModelCallback(self.model, monitor=self.metric, mode=save_callback_mode, name=self.name)
            with progress_disabled_ctx(self.model) as model:
                original_path = model.path
                model.path = Path(temp_dir)
                model.fit_one_cycle(self.epochs, self.lr, callbacks=save_callback)

                # Load the best one and export it
                model.load(self.name)
                print(f'Model validation metrics: {model.validate()}')
                model.path = original_path\
        """