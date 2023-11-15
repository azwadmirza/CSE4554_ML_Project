    def get_recipe_sources(self, conan_reference, export_folder, export_sources_folder, remote):
        t1 = time.time()

        def filter_function(urls):
            file_url = urls.get(EXPORT_SOURCES_TGZ_NAME)
            if file_url:
                urls = {EXPORT_SOURCES_TGZ_NAME: file_url}
            else:
                return None
            return urls

        zipped_files = self._call_remote(remote, "get_recipe",
                                         conan_reference, export_folder, filter_function)
        duration = time.time() - t1
        log_recipe_sources_download(conan_reference, duration, remote, zipped_files)

        if not zipped_files:
            mkdir(export_sources_folder)  # create the folder even if no source files
            return

        unzip_and_get_files(zipped_files, export_sources_folder, EXPORT_SOURCES_TGZ_NAME)
        c_src_path = os.path.join(export_sources_folder, ".c_src")
        if os.path.exists(c_src_path):
            merge_directories(c_src_path, export_sources_folder)
            shutil.rmtree(c_src_path)
        for dirname, _, filenames in os.walk(export_sources_folder):
            for fname in filenames:
                touch(os.path.join(dirname, fname))