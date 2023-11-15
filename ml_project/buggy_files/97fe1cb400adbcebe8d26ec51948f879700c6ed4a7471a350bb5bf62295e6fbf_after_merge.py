  def _split_generators(self, dl_manager):
    """Returns SplitGenerators."""
    cfg = self.builder_config
    download_urls = {
        cfg.name: '/'.join([_DOWNLOAD_URL, 'data', cfg.name + '.jsonl'])
    }

    downloaded_files = dl_manager.download_and_extract(download_urls)

    return [
        tfds.core.SplitGenerator(
            name=tfds.Split.TRAIN,
            gen_kwargs={'filepath': downloaded_files[cfg.name]})
    ]