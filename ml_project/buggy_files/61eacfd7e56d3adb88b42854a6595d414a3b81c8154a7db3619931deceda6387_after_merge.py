    def distill(self, X_train=None, y_train=None, X_val=None, y_val=None,
                time_limits=None, hyperparameters=None, holdout_frac=None, verbosity=None,
                models_name_suffix=None, teacher_preds='soft',
                augmentation_data=None, augment_method='spunge', augment_args={'size_factor':5,'max_size':int(1e5)}):
        """ Various distillation algorithms.
            Args:
                X_train, y_train: pd.DataFrame and pd.Series of training data.
                    If None, original training data used during TabularPrediction.fit() will be loaded.
                    This data is split into train/validation if X_val, y_val are None.
                X_val, y_val: pd.DataFrame and pd.Series of validation data.
                time_limits, hyperparameters, holdout_frac: defined as in TabularPrediction.fit()
                teacher_preds (None or str): If None, we only train with original labels (no data augmentation, overrides augment_method)
                    If 'hard', labels are hard teacher predictions given by: teacher.predict()
                    If 'soft', labels are soft teacher predictions given by: teacher.predict_proba()
                    Note: 'hard' and 'soft' are equivalent for regression problems.
                    If augment_method specified, teacher predictions are only used to label augmented data (training data keeps original labels).
                    To apply label-smoothing: teacher_preds='onehot' will use original training data labels converted to one-hots for multiclass (no data augmentation).  # TODO: expose smoothing-hyperparameter.
                models_name_suffix (str): Suffix to append to each student model's name, new names will look like: 'MODELNAME_dstl_SUFFIX'
                augmentation_data: pd.DataFrame of additional data to use as "augmented data" (does not contain labels).
                    When specified, augment_method, augment_args are ignored, and this is the only augmented data that is used (teacher_preds cannot be None).
                augment_method (None or str): specifies which augmentation strategy to utilize. Options: [None, 'spunge','munge']
                    If None, no augmentation gets applied.
                }
                augment_args (dict): args passed into the augmentation function corresponding to augment_method.
        """
        if verbosity is None:
            verbosity = self.verbosity

        hyperparameter_tune = False  # TODO: add as argument with scheduler options.
        if augmentation_data is not None and teacher_preds is None:
            raise ValueError("augmentation_data must be None if teacher_preds is None")

        logger.log(20, f"Distilling with teacher_preds={str(teacher_preds)}, augment_method={str(augment_method)} ...")
        if X_train is None:
            if y_train is not None:
                raise ValueError("X cannot be None when y specified.")
            X_train = self.load_X_train()
            if not self.bagged_mode:
                try:
                    X_val = self.load_X_val()
                except FileNotFoundError:
                    pass

        if y_train is None:
            y_train = self.load_y_train()
            if not self.bagged_mode:
                try:
                    y_val = self.load_y_val()
                except FileNotFoundError:
                    pass

        if X_val is None:
            if y_val is not None:
                raise ValueError("X_val cannot be None when y_val specified.")
            if holdout_frac is None:
                holdout_frac = default_holdout_frac(len(X_train), hyperparameter_tune)
            X_train, X_val, y_train, y_val = generate_train_test_split(X_train, y_train, problem_type=self.problem_type, test_size=holdout_frac)

        y_val_og = y_val.copy()
        og_bagged_mode = self.bagged_mode
        og_verbosity = self.verbosity
        self.bagged_mode = False  # turn off bagging
        self.verbosity = verbosity  # change verbosity for distillation

        if teacher_preds is None or teacher_preds == 'onehot':
            augment_method = None
            logger.log(20, "Training students without a teacher model. Set teacher_preds = 'soft' or 'hard' to distill using the best AutoGluon predictor as teacher.")

        if teacher_preds in ['onehot','soft']:
            y_train = format_distillation_labels(y_train, self.problem_type, self.num_classes)
            y_val = format_distillation_labels(y_val, self.problem_type, self.num_classes)

        if augment_method is None and augmentation_data is None:
            if teacher_preds == 'hard':
                y_pred = pd.Series(self.predict(X_train))
                if (self.problem_type != REGRESSION) and (len(y_pred.unique()) < len(y_train.unique())):  # add missing labels
                    logger.log(15, "Adding missing labels to distillation dataset by including some real training examples")
                    indices_to_add = []
                    for clss in y_train.unique():
                        if clss not in y_pred.unique():
                            logger.log(15, f"Fetching a row with label={clss} from training data")
                            clss_index = y_train[y_train == clss].index[0]
                            indices_to_add.append(clss_index)
                    X_extra = X_train.loc[indices_to_add].copy()
                    y_extra = y_train.loc[indices_to_add].copy()  # these are actually real training examples
                    X_train = pd.concat([X_train, X_extra])
                    y_pred = pd.concat([y_pred, y_extra])
                y_train = y_pred
            elif teacher_preds == 'soft':
                y_train = self.predict_proba(X_train)
                if self.problem_type == MULTICLASS:
                    y_train = pd.DataFrame(y_train)
                else:
                    y_train = pd.Series(y_train)
        else:
            X_aug = augment_data(X_train=X_train, feature_metadata=self.feature_metadata,
                                augmentation_data=augmentation_data, augment_method=augment_method, augment_args=augment_args)
            if len(X_aug) > 0:
                if teacher_preds == 'hard':
                    y_aug = pd.Series(self.predict(X_aug))
                elif teacher_preds == 'soft':
                    y_aug = self.predict_proba(X_aug)
                    if self.problem_type == MULTICLASS:
                        y_aug = pd.DataFrame(y_aug)
                    else:
                        y_aug = pd.Series(y_aug)
                else:
                    raise ValueError(f"Unknown teacher_preds specified: {teacher_preds}")

                X_train = pd.concat([X_train, X_aug])
                y_train = pd.concat([y_train, y_aug])

        X_train.reset_index(drop=True, inplace=True)
        y_train.reset_index(drop=True, inplace=True)

        student_suffix = '_DSTL'  # all student model names contain this substring
        if models_name_suffix is not None:
            student_suffix = student_suffix + "_" + models_name_suffix

        if hyperparameters is None:
            hyperparameters = copy.deepcopy(self.hyperparameters)
            student_model_types = ['GBM','CAT','NN','RF']  # only model types considered for distillation
            default_level_key = 'default'
            if default_level_key in hyperparameters:
                hyperparameters[default_level_key] = {key: hyperparameters[default_level_key][key] for key in hyperparameters[default_level_key] if key in student_model_types}
            else:
                hyperparameters ={key: hyperparameters[key] for key in hyperparameters if key in student_model_types}
                if len(hyperparameters) == 0:
                    raise ValueError("Distillation not yet supported for fit() with per-stack level hyperparameters. "
                        "Please either manually specify `hyperparameters` in `distill()` or call `fit()` again without per-level hyperparameters before distillation."
                        "Also at least one of the following model-types must be present in hyperparameters: ['GBM','CAT','NN','RF']")
        else:
            hyperparameters = self._process_hyperparameters(hyperparameters=hyperparameters, ag_args_fit=None, excluded_model_types=None)  # TODO: consider exposing ag_args_fit, excluded_model_types as distill() arguments.
        if teacher_preds is None or teacher_preds == 'hard':
            models_distill = get_preset_models(path=self.path, problem_type=self.problem_type,
                                eval_metric=self.eval_metric, stopping_metric=self.stopping_metric,
                                num_classes=self.num_classes, hyperparameters=hyperparameters, name_suffix=student_suffix)
        else:
            models_distill = get_preset_models_distillation(path=self.path, problem_type=self.problem_type,
                                eval_metric=self.eval_metric, stopping_metric=self.stopping_metric,
                                num_classes=self.num_classes, hyperparameters=hyperparameters, name_suffix=student_suffix)
            if self.problem_type != REGRESSION:
                self.regress_preds_asprobas = True

        self.time_train_start = time.time()
        self.time_limit = time_limits
        distilled_model_names = []
        for model in models_distill:
            time_left = None
            if time_limits is not None:
                time_start_model = time.time()
                time_left = time_limits - (time_start_model - self.time_train_start)

            logger.log(15, f"Distilling student {str(model.name)} with teacher_preds={str(teacher_preds)}, augment_method={str(augment_method)}...")
            models = self.train_single_full(X_train=X_train, y_train=y_train, X_val=X_val, y_val=y_val, model=model,
                                            hyperparameter_tune=False, stack_name=self.distill_stackname, time_limit=time_left)
            for model_name in models:  # finally measure original metric on validation data and overwrite stored val_scores
                model_score = self.score(X_val, y_val_og, model=model_name)
                self.model_performance[model_name] = model_score
                model_obj = self.load_model(model_name)
                model_obj.val_score = model_score
                model_obj.save()  # TODO: consider omitting for sake of efficiency
                self.model_graph.nodes[model_name]['val_score'] = model_score
                distilled_model_names.append(model_name)
                logger.log(20, '\t' + str(round(model_obj.val_score, 4)) + '\t = Validation ' + self.eval_metric.name + ' score')
        # reset trainer to old state before distill() was called:
        self.bagged_mode = og_bagged_mode  # TODO: Confirm if safe to train future models after training models in both bagged and non-bagged modes
        self.verbosity = og_verbosity
        return distilled_model_names