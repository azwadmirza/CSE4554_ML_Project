  def _split_generators(self, dl_manager):
    """Returns SplitGenerators."""

    del dl_manager  # Unused

    lang = self._builder_config.language

    return [
        tfds.core.SplitGenerator(
            name=tfds.Split.TRAIN,
            gen_kwargs={
                "filepaths": "%s/train/%s_examples-*" % (_DATA_DIRECTORY,
                                                         lang)},
        ),
        tfds.core.SplitGenerator(
            name=tfds.Split.VALIDATION,
            gen_kwargs={"filepaths": "%s/dev/%s_examples-*" % (_DATA_DIRECTORY,
                                                               lang)},
        ),
        tfds.core.SplitGenerator(
            name=tfds.Split.TEST,
            gen_kwargs={"filepaths": "%s/test/%s_examples-*" % (_DATA_DIRECTORY,
                                                                lang)},
        ),
    ]