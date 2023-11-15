    def _set_paths(self, handle, path):
        """Parses relevant hdf5-paths out of ``handle``.

        Parameters
        ----------
        handle : h5py.File
        path : str
            (absolute) filepath for current hdf5 container
        """
        iterations = []
        encoding = handle.attrs["iterationEncoding"].decode()
        if "groupBased" in encoding:
            iterations = list(handle["/data"].keys())
            mylog.info("open_pmd - found {} iterations in file".format(len(iterations)))
        elif "fileBased" in encoding:
            itformat = handle.attrs["iterationFormat"].decode().split("/")[-1]
            regex = "^" + itformat.replace("%T", "[0-9]+") + "$"
            if path is "":
                mylog.warning("open_pmd - For file based iterations, please use absolute file paths!")
                pass
            for filename in listdir(path):
                if match(regex, filename):
                    iterations.append(filename)
            mylog.info("open_pmd - found {} iterations in directory".format(len(iterations)))

        if len(iterations) == 0:
            mylog.warning("open_pmd - no iterations found!")
        if "groupBased" in encoding and len(iterations) > 1:
            mylog.warning("open_pmd - only choose to load one iteration ({})".format(list(handle["/data"].keys())[0]))

        self.base_path = "/data/{}/".format(list(handle["/data"].keys())[0])
        self.meshes_path = self._handle["/"].attrs["meshesPath"].decode()
        self.particles_path = self._handle["/"].attrs["particlesPath"].decode()