    def __init__(self, key_phrase="hey mycroft", config=None, lang="en-us"):
        super().__init__(key_phrase, config, lang)
        keyword_file_paths = [expanduser(x.strip()) for x in self.config.get(
            "keyword_file_path", "hey_mycroft.ppn").split(',')]
        sensitivities = self.config.get("sensitivities", 0.5)

        try:
            from pvporcupine.porcupine import Porcupine
            from pvporcupine.util import (pv_library_path,
                                          pv_model_path)
        except ImportError as err:
            raise Exception(
                "Python bindings for Porcupine not found. "
                "Please run \"mycroft-pip install pvporcupine\"") from err

        library_path = pv_library_path('')
        model_file_path = pv_model_path('')
        if isinstance(sensitivities, float):
            sensitivities = [sensitivities] * len(keyword_file_paths)
        else:
            sensitivities = [float(x) for x in sensitivities.split(',')]

        self.audio_buffer = []
        self.has_found = False
        self.num_keywords = len(keyword_file_paths)

        LOG.warning('The Porcupine wakeword engine shipped with '
                    'Mycroft-core is deprecated and will be removed in '
                    'mycroft-core 21.02. Use the mycroft-porcupine-plugin '
                    'instead.')
        LOG.info(
            'Loading Porcupine using library path {} and keyword paths {}'
            .format(library_path, keyword_file_paths))
        self.porcupine = Porcupine(
            library_path=library_path,
            model_path=model_file_path,
            keyword_paths=keyword_file_paths,
            sensitivities=sensitivities)

        LOG.info('Loaded Porcupine')