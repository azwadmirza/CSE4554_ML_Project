    def __ensure_cache_file(self):
        if self.__image_cache_file is None:
            path = cpprefs.get_temporary_directory()
            if (path is None) or (not os.path.exists(path)) or \
               (not os.access(path, os.W_OK)):
                path = None
            h, self.__image_cache_path = tempfile.mkstemp(
                dir = path,
                suffix=".h5", 
                prefix="CellProfilerImageCache")
            self.__image_cache_file = h5py.File(
                self.__image_cache_path, "w")
            self.__hdf5_object_set = HDF5ObjectSet(self.__image_cache_file)
            os.close(h)