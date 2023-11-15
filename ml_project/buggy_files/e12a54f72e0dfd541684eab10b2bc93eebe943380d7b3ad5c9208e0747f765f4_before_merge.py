    def get_embedded_classes(self):
        """
        Get the list of Java classes from all DEX files.

        :return: list of Java classes
        """
        if self.classes is not None:
            return self.classes
        for dex_file in glob.iglob(os.path.join(self.apk_dir, '*.dex')):
            if (len(settings.BACKSMALI_BINARY) > 0
                    and is_file_exists(settings.BACKSMALI_BINARY)):
                bs_path = settings.BACKSMALI_BINARY
            else:
                bs_path = os.path.join(self.tools_dir, 'baksmali-2.4.0.jar')
            args = [settings.JAVA_BINARY, '-jar',
                    bs_path, 'list', 'classes', dex_file]
            classes = subprocess.check_output(
                args, universal_newlines=True).splitlines()
            if self.classes is not None:
                self.classes = self.classes + classes
            else:
                self.classes = classes
        return self.classes