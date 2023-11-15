    def _load_intents(config):
        intent_file = os.path.join(config["install_path"], "intents.yml")
        if os.path.isfile(intent_file):
            with open(intent_file, 'r') as intent_file_handle:
                intents = intent_file_handle.read()
                return intents
        else:
            return None