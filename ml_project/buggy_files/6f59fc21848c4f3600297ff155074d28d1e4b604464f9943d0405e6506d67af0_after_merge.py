    def load_json(self, fn, cs):
        """Load and runhistory in json representation from disk.

        Overwrites current runthistory!

        Parameters
        ----------
        fn : str
            file name to load from
        cs : ConfigSpace
            instance of configuration space
        """

        with open(fn) as fp:
            all_data = json.load(fp)

        self.ids_config = {int(id_): Configuration(cs, values=values)
                           for id_, values in all_data["configs"].items()}


        self.config_ids = {Configuration(cs, values=values): int(id_)
                           for id_, values in all_data["configs"].items()}

        self._n_id = len(self.config_ids)
        
        self.data = {self.RunKey(int(k[0]), k[1], int(k[2])):
                     self.RunValue(float(v[0]), float(v[1]), v[2], v[3])
                     for k, v in all_data["data"]}