  def _split_generators(self, dl_manager):
    """Returns SplitGenerators."""

    del dl_manager  # Unused

    lang = self._builder_config.language

    return [
        tfds.core.SplitGenerator(
            name=tfds.Split.TRAIN,
            gen_kwargs={
                "filepaths": os.path.join(
                    _DATA_DIRECTORY, "train", "{}_examples-*".format(lang))},
        ),
        tfds.core.SplitGenerator(
            name=tfds.Split.VALIDATION,
            gen_kwargs={
                "filepaths": os.path.join(
                    _DATA_DIRECTORY, "dev", "{}_examples-*".format(lang))}
        ),
        tfds.core.SplitGenerator(
            name=tfds.Split.TEST,
            gen_kwargs={
                "filepaths": os.path.join(
                    _DATA_DIRECTORY, "test", "{}_examples-*".format(lang))}
        ),
    ]