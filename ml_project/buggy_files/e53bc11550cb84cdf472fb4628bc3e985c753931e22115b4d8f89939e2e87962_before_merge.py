    def get_translation_strings(self):
        # type: () -> Dict[str, str]
        translation_strings = {} # type: Dict[str, str]
        dirname = self.get_template_dir()

        for dirpath, dirnames, filenames in os.walk(dirname):
            for filename in [f for f in filenames if f.endswith(".handlebars")]:
                with open(os.path.join(dirpath, filename), 'r') as reader:
                    data = reader.read()
                    data = data.replace('\n', '\\n')
                    translation_strings.update(self.extract_strings(data))

        dirname = os.path.join(settings.DEPLOY_ROOT, 'static/js')
        for filename in os.listdir(dirname):
            if filename.endswith('.js'):
                with open(os.path.join(dirname, filename)) as reader:
                    data = reader.read()
                    translation_strings.update(self.extract_strings(data))

        return translation_strings