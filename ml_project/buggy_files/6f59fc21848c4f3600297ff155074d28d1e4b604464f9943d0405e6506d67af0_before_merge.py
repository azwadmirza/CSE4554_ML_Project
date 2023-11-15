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

        self.ids_config = dict([(int(id_), Configuration(
            cs, vector=numpy.array(vec))) for id_, vec in all_data["id_config"].items()])


        self.config_ids = dict([(Configuration(
            cs, vector=numpy.array(vec)).__repr__(), id_) for id_, vec in all_data["id_config"].items()])
        self._n_id = len(self.config_ids)
        
        self.data = dict([(self.RunKey(int(k[0]), k[1], int(k[2])),
                           self.RunValue(float(v[0]), float(v[1]), v[2], v[3]))
                          for k, v in all_data["data"]
                          ])