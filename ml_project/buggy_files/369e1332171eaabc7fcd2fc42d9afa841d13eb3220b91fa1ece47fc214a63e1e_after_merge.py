    def _set_paths(self, handle, path, iteration):
        """Parses relevant hdf5-paths out of ``handle``.

        Parameters
        ----------
        handle : h5py.File
        path : str
            (absolute) filepath for current hdf5 container
        """
        iterations = []
        if iteration is None:
            iteration = list(handle["/data"].keys())[0]
        encoding = handle.attrs["iterationEncoding"].decode()
        if "groupBased" in encoding:
            iterations = list(handle["/data"].keys())
            mylog.info("Found {} iterations in file".format(len(iterations)))
        elif "fileBased" in encoding:
            itformat = handle.attrs["iterationFormat"].decode().split("/")[-1]
            regex = "^" + itformat.replace("%T", "[0-9]+") + "$"
            if path is "":
                mylog.warning("For file based iterations, please use absolute file paths!")
                pass
            for filename in listdir(path):
                if match(regex, filename):
                    iterations.append(filename)
            mylog.info("Found {} iterations in directory".format(len(iterations)))

        if len(iterations) == 0:
            mylog.warning("No iterations found!")
        if "groupBased" in encoding and len(iterations) > 1:
            mylog.warning("Only chose to load one iteration ({})".format(iteration))

        self.base_path = "/data/{}/".format(iteration)
        self.meshes_path = self._handle["/"].attrs["meshesPath"].decode()
        try:
            handle[self.base_path + self.meshes_path]
        except(KeyError):
            if self.standard_version <= StrictVersion("1.1.0"):
                mylog.info("meshesPath not present in file."
                           " Assuming file contains no meshes and has a domain extent of 1m^3!")
            else:
                raise
        self.particles_path = self._handle["/"].attrs["particlesPath"].decode()
        try:
            handle[self.base_path + self.particles_path]
        except(KeyError):
            if self.standard_version <= StrictVersion("1.1.0"):
                mylog.info("particlesPath not present in file."
                           " Assuming file contains no particles!")
            else:
                raise