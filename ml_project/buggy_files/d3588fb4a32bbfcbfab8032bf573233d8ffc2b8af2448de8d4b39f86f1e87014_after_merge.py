    def _transform_arguments(self):
        self.n_features = len(self.feature_dict)
        self.feature_array = None

        if self.overall_obj[:3] in ["PAR", "par"]:
            par_str = self.overall_obj[3:]
        elif self.overall_obj[:4] in ["mean", "MEAN"]:
            par_str = self.overall_obj[4:]
        # Check for par-value as in "par10"/ "mean5"
        if len(par_str) > 0:
            self.par_factor = int(par_str)
        else:
            self.logger.debug("No par-factor detected. Using 1 by default.")
            self.par_factor = 1

        # read instance files
        if self.train_inst_fn:
            if os.path.isfile(self.train_inst_fn):
                self.train_insts = self.in_reader.read_instance_file(
                    self.train_inst_fn)
            else:
                self.logger.error(
                    "Have not found instance file: %s" % (self.train_inst_fn))
                sys.exit(1)
        if self.test_inst_fn:
            if os.path.isfile(self.test_inst_fn):
                self.test_insts = self.in_reader.read_instance_file(
                    self.test_inst_fn)
            else:
                self.logger.error(
                    "Have not found test instance file: %s" % (
                        self.test_inst_fn))
                sys.exit(1)

        self.instance_specific = {}

        def extract_instance_specific(instance_list):
            insts = []
            for inst in instance_list:
                if len(inst) > 1:
                    self.instance_specific[inst[0]] = " ".join(inst[1:])
                insts.append(inst[0])
            return insts

        self.train_insts = extract_instance_specific(self.train_insts)
        if self.test_insts:
            self.test_insts = extract_instance_specific(self.test_insts)

        # read feature file
        if self.feature_fn:
            if os.path.isfile(self.feature_fn):
                self.feature_dict = self.in_reader.read_instance_features_file(
                    self.feature_fn)[1]

        if self.feature_dict:
            self.feature_array = []
            for inst_ in self.train_insts:
                self.feature_array.append(self.feature_dict[inst_])
            self.feature_array = numpy.array(self.feature_array)
            self.n_features = self.feature_array.shape[1]

            # reduce dimensionality of features of larger than PCA_DIM
            if self.feature_array.shape[1] > self.PCA_DIM:
                X = self.feature_array
                # scale features
                X = MinMaxScaler().fit_transform(X)
                X = numpy.nan_to_num(X) # if features with max == min
                #PCA
                pca = PCA(n_components=self.PCA_DIM)
                self.feature_array = pca.fit_transform(X)
                self.n_features = self.feature_array.shape[1]
                # update feature dictionary
                for feat, inst_ in zip(self.feature_array, self.train_insts):
                    self.feature_dict[inst_] = feat

        # read pcs file
        if self.pcs_fn and os.path.isfile(self.pcs_fn):
            with open(self.pcs_fn) as fp:
                pcs_str = fp.readlines()
                self.cs = pcs.read(pcs_str)
                self.cs.seed(42)
        elif self.pcs_fn:
            self.logger.error("Have not found pcs file: %s" %
                              (self.pcs_fn))
            sys.exit(1)

        # you cannot set output dir to None directly
        # because None is replaced by default always
        if self.output_dir == "":
            self.output_dir = None
            self.logger.debug("Deactivate output directory.")
        else:
            self.logger.info("Output to %s" % (self.output_dir))