    def get_writer(self, writer="geotiff", **kwargs):
        config_fn = writer + ".yaml" if "." not in writer else writer
        config_files = config_search_paths(
            os.path.join("writers", config_fn), self.ppp_config_dir)
        kwargs.setdefault("config_files", config_files)
        return self.load_writer_config(**kwargs)