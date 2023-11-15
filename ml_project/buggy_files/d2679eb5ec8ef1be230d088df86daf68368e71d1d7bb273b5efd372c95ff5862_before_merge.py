    def fit_summary(self, verbosity=3):
        """
            Output summary of information about models produced during `fit()`.
            May create various generated summary plots and store them in folder: `Predictor.output_directory`.

            Parameters
            ----------
            verbosity : int, default = 3
                Controls how detailed of a summary to ouput.
                Set <= 0 for no output printing, 1 to print just high-level summary,
                2 to print summary and create plots, >= 3 to print all information produced during fit().

            Returns
            -------
            Dict containing various detailed information. We do not recommend directly printing this dict as it may be very large.
        """
        hpo_used = len(self._trainer.hpo_results) > 0
        model_typenames = {key: self._trainer.model_types[key].__name__ for key in self._trainer.model_types}
        model_innertypenames = {key: self._trainer.model_types_inner[key].__name__ for key in self._trainer.model_types if key in self._trainer.model_types_inner}
        MODEL_STR = 'Model'
        ENSEMBLE_STR = 'Ensemble'
        for model in model_typenames:
            if (model in model_innertypenames) and (ENSEMBLE_STR not in model_innertypenames[model]) and (ENSEMBLE_STR in model_typenames[model]):
                new_model_typename = model_typenames[model] + "_" + model_innertypenames[model]
                if new_model_typename.endswith(MODEL_STR):
                    new_model_typename = new_model_typename[:-len(MODEL_STR)]
                model_typenames[model] = new_model_typename

        unique_model_types = set(model_typenames.values())  # no more class info
        # all fit() information that is returned:
        results = {
            'model_types': model_typenames,  # dict with key = model-name, value = type of model (class-name)
            'model_performance': self._trainer.get_model_attributes_dict('val_score'),  # dict with key = model-name, value = validation performance
            'model_best': self._trainer.model_best,  # the name of the best model (on validation data)
            'model_paths': self._trainer.model_paths,  # dict with key = model-name, value = path to model file
            'model_fit_times': self._trainer.get_model_attributes_dict('fit_time'),
            'model_pred_times': self._trainer.get_model_attributes_dict('predict_time'),
            'num_bagging_folds': self._trainer.kfolds,
            'stack_ensemble_levels': self._trainer.stack_ensemble_levels,
            'feature_prune': self._trainer.feature_prune,
            'hyperparameter_tune': hpo_used,
            'hyperparameters_userspecified': self._trainer.hyperparameters,
        }
        if self.problem_type != REGRESSION:
            results['num_classes'] = self._trainer.num_classes
        if hpo_used:
            results['hpo_results'] = self._trainer.hpo_results
        # get dict mapping model name to final hyperparameter values for each model:
        model_hyperparams = {}
        for model_name in self._trainer.get_model_names_all():
            model_obj = self._trainer.load_model(model_name)
            model_hyperparams[model_name] = model_obj.params
        results['model_hyperparams'] = model_hyperparams

        if verbosity > 0:  # print stuff
            print("*** Summary of fit() ***")
            print("Estimated performance of each model:")
            results['leaderboard'] = self._learner.leaderboard(silent=False)
            # self._summarize('model_performance', 'Validation performance of individual models', results)
            #  self._summarize('model_best', 'Best model (based on validation performance)', results)
            # self._summarize('hyperparameter_tune', 'Hyperparameter-tuning used', results)
            print("Number of models trained: %s" % len(results['model_performance']))
            print("Types of models trained:")
            print(unique_model_types)
            num_fold_str = ""
            bagging_used = results['num_bagging_folds'] > 0
            if bagging_used:
                num_fold_str = f" (with {results['num_bagging_folds']} folds)"
            print("Bagging used: %s %s" % (bagging_used, num_fold_str))
            num_stack_str = ""
            stacking_used = results['stack_ensemble_levels'] > 0
            if stacking_used:
                num_stack_str = f" (with {results['stack_ensemble_levels']} levels)"
            print("Stack-ensembling used: %s %s" % (stacking_used, num_stack_str))
            hpo_str = ""
            if hpo_used and verbosity <= 2:
                hpo_str = " (call fit_summary() with verbosity >= 3 to see detailed HPO info)"
            print("Hyperparameter-tuning used: %s %s" % (hpo_used, hpo_str))
            # TODO: uncomment once feature_prune is functional:  self._summarize('feature_prune', 'feature-selection used', results)
            print("User-specified hyperparameters:")
            print(results['hyperparameters_userspecified'])
        if verbosity > 1:  # create plots
            plot_tabular_models(results, output_directory=self.output_directory,
                                save_file="SummaryOfModels.html",
                                plot_title="Models produced during fit()")
            if hpo_used:
                for model_type in results['hpo_results']:
                    if 'trial_info' in results['hpo_results'][model_type]:
                        plot_summary_of_models(
                            results['hpo_results'][model_type],
                            output_directory=self.output_directory, save_file=model_type + "_HPOmodelsummary.html",
                            plot_title=f"Models produced during {model_type} HPO")
                        plot_performance_vs_trials(
                            results['hpo_results'][model_type],
                            output_directory=self.output_directory, save_file=model_type + "_HPOperformanceVStrials.png",
                            plot_title=f"HPO trials for {model_type} models")
        if verbosity > 2:  # print detailed information
            if hpo_used:
                hpo_results = results['hpo_results']
                print("*** Details of Hyperparameter optimization ***")
                for model_type in hpo_results:
                    hpo_model = hpo_results[model_type]
                    print("HPO for %s model:  Num. configurations tried = %s, Time spent = %s, Search strategy = %s"
                          % (model_type, len(hpo_model['trial_info']), hpo_model['total_time'], hpo_model['search_strategy']))
                    print("Best hyperparameter-configuration (validation-performance: %s = %s):"
                          % (self.eval_metric, hpo_model['validation_performance']))
                    print(hpo_model['best_config'])
            """
            if bagging_used:
                pass # TODO: print detailed bagging info
            if stacking_used:
                pass # TODO: print detailed stacking info, like how much it improves validation performance
            if results['feature_prune']:
                pass # TODO: print detailed feature-selection info once feature-selection is functional.
            """
        if verbosity > 0:
            print("*** End of fit() summary ***")
        return results