    def hyperparameter_tune(self, X_train, y_train, X_val, y_val, scheduler_options, **kwargs):
        time_start = time.time()
        """ Performs HPO and sets self.params to best hyperparameter values """
        self.verbosity = kwargs.get('verbosity', 2)
        logger.log(15, "Beginning hyperparameter tuning for Neural Network...")
        self._set_default_searchspace() # changes non-specified default hyperparams from fixed values to search-spaces.
        if self.feature_metadata is None:
            raise ValueError("Trainer class must set feature_metadata for this model")
        scheduler_func = scheduler_options[0]
        scheduler_options = scheduler_options[1]
        if scheduler_func is None or scheduler_options is None:
            raise ValueError("scheduler_func and scheduler_options cannot be None for hyperparameter tuning")
        num_cpus = scheduler_options['resource']['num_cpus']
        # num_gpus = scheduler_options['resource']['num_gpus']  # TODO: Currently unused

        params_copy = self.params.copy()

        self.num_dataloading_workers = max(1, int(num_cpus/2.0))
        self.batch_size = params_copy['batch_size']
        train_dataset, val_dataset = self.generate_datasets(X_train=X_train, y_train=y_train, params=params_copy, X_val=X_val, y_val=y_val)
        train_path = self.path + "train"
        val_path = self.path + "validation"
        train_dataset.save(file_prefix=train_path)
        val_dataset.save(file_prefix=val_path)

        if not np.any([isinstance(params_copy[hyperparam], Space) for hyperparam in params_copy]):
            logger.warning("Warning: Attempting to do hyperparameter optimization without any search space (all hyperparameters are already fixed values)")
        else:
            logger.log(15, "Hyperparameter search space for Neural Network: ")
            for hyperparam in params_copy:
                if isinstance(params_copy[hyperparam], Space):
                    logger.log(15, str(hyperparam)+ ":   "+str(params_copy[hyperparam]))

        util_args = dict(
            train_path=train_path,
            val_path=val_path,
            model=self,
            time_start=time_start,
            time_limit=scheduler_options['time_out']
        )
        tabular_nn_trial.register_args(util_args=util_args, **params_copy)
        scheduler = scheduler_func(tabular_nn_trial, **scheduler_options)
        if ('dist_ip_addrs' in scheduler_options) and (len(scheduler_options['dist_ip_addrs']) > 0):
            # TODO: Ensure proper working directory setup on remote machines
            # This is multi-machine setting, so need to copy dataset to workers:
            logger.log(15, "Uploading preprocessed data to remote workers...")
            scheduler.upload_files([train_path+TabularNNDataset.DATAOBJ_SUFFIX,
                                train_path+TabularNNDataset.DATAVALUES_SUFFIX,
                                val_path+TabularNNDataset.DATAOBJ_SUFFIX,
                                val_path+TabularNNDataset.DATAVALUES_SUFFIX])  # TODO: currently does not work.
            logger.log(15, "uploaded")

        scheduler.run()
        scheduler.join_jobs()
        scheduler.get_training_curves(plot=False, use_legend=False)

        return self._get_hpo_results(scheduler=scheduler, scheduler_options=scheduler_options, time_start=time_start)