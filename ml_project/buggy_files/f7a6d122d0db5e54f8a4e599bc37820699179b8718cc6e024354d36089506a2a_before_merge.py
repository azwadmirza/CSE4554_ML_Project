    def import_data(self, data):
        """
        Import additional data for tuning.

        Parameters
        ----------
        data : list of dict
            Each of which has at least two keys, ``parameter`` and ``value``.
        """
        _completed_num = 0
        for trial_info in data:
            self.logger.info("Importing data, current processing progress %s / %s", _completed_num, len(data))
            # simply validate data format
            assert "parameter" in trial_info
            _params = trial_info["parameter"]
            assert "value" in trial_info
            _value = trial_info['value']
            if not _value:
                self.logger.info("Useless trial data, value is %s, skip this trial data.", _value)
                continue
            # convert the keys in loguniform and categorical types
            valid_entry = True
            for key, value in _params.items():
                if key in self.loguniform_key:
                    _params[key] = np.log(value)
                elif key in self.categorical_dict:
                    if value in self.categorical_dict[key]:
                        _params[key] = self.categorical_dict[key].index(value)
                    else:
                        self.logger.info("The value %s of key %s is not in search space.", str(value), key)
                        valid_entry = False
                        break
            if not valid_entry:
                continue
            # start import this data entry
            _completed_num += 1
            config = Configuration(self.cs, values=_params)
            if self.optimize_mode is OptimizeMode.Maximize:
                _value = -_value
            if self.first_one:
                self.smbo_solver.nni_smac_receive_first_run(config, _value)
                self.first_one = False
            else:
                self.smbo_solver.nni_smac_receive_runs(config, _value)
        self.logger.info("Successfully import data to smac tuner, total data: %d, imported data: %d.", len(data), _completed_num)