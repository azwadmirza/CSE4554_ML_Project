    def save_json(self, fn="runhistory.json"):
        '''
        saves runhistory on disk

        Parameters
        ----------
        fn : str
            file name
        '''

        configs = {id_: conf.get_dictionary()
                   for id_, conf in self.ids_config.items()}

        data = [([int(k.config_id),
                  str(k.instance_id) if k.instance_id is not None else None,
                  int(k.seed)], list(v))
                for k, v in self.data.items()]

        with open(fn, "w") as fp:
            json.dump({"data": data,
                       "configs": configs}, fp)