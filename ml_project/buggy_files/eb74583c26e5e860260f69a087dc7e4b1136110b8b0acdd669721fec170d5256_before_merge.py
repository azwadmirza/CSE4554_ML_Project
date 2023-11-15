    def add(self, config, cost, time,
            status, instance_id=None,
            seed=None,
            additional_info=None):
        '''
        adds a data of a new target algorithm (TA) run;
        it will update data if the same key values are used 
        (config, instance_id, seed)

        Attributes
        ----------
            config : dict (or other type -- depending on config space module)
                parameter configuratoin
            cost: float
                cost of TA run (will be minimized)
            time: float
                runtime of TA run
            status: str
                status in {SUCCESS, TIMEOUT, CRASHED, ABORT, MEMOUT}
            instance_id: str
                str representing an instance (default: None)
            seed: int
                random seed used by TA (default: None)
            additional_info: dict
                additional run infos (could include further returned
                information from TA or fields such as start time and host_id)
        '''

        # TODO: replace str casting of config when we have something hashable
        # as a config object
        # TODO JTS: We might have to execute one config multiple times
        #           since the results can be noisy and then we can't simply
        #           overwrite the old config result here!
        config_id = self.config_ids.get(config.__repr__())
        if config_id is None:
            self._n_id += 1
            self.config_ids[config.__repr__()] = self._n_id
            config_id = self.config_ids.get(config.__repr__())
            self.ids_config[self._n_id] = config

        k = self.RunKey(config_id, instance_id, seed)
        v = self.RunValue(cost, time, status, additional_info)

        self.data[k] = v