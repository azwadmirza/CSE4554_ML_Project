    def __init__(self, key_phrase="hey mycroft", config=None, lang="en-us"):
        super(PorcupineHotWord, self).__init__(key_phrase, config, lang)
        porcupine_path = expanduser(self.config.get(
            "porcupine_path", join('~', '.mycroft', 'Porcupine')))
        keyword_file_paths = [expanduser(x.strip()) for x in self.config.get(
            "keyword_file_path", "hey_mycroft.ppn").split(',')]
        sensitivities = self.config.get("sensitivities", 0.5)
        bindings_path = join(porcupine_path, 'binding/python')
        LOG.info('Adding %s to Python path' % bindings_path)
        sys.path.append(bindings_path)
        try:
            from porcupine import Porcupine
        except ImportError:
            raise Exception(
                "Python bindings for Porcupine not found. "
                "Please use --porcupine-path to set Porcupine base path")

        system = platform.system()
        machine = platform.machine()
        library_path = join(
            porcupine_path, 'lib/linux/%s/libpv_porcupine.so' % machine)
        model_file_path = join(
            porcupine_path, 'lib/common/porcupine_params.pv')
        if isinstance(sensitivities, float):
            sensitivities = [sensitivities] * len(keyword_file_paths)
        else:
            sensitivities = [float(x) for x in sensitivities.split(',')]

        self.audio_buffer = []
        self.has_found = False
        self.num_keywords = len(keyword_file_paths)
        LOG.info(
            'Loading Porcupine using library path {} and keyword paths {}'
            .format(library_path, keyword_file_paths))
        self.porcupine = Porcupine(
            library_path=library_path,
            model_file_path=model_file_path,
            keyword_file_paths=keyword_file_paths,
            sensitivities=sensitivities)

        LOG.info('Loaded Porcupine')