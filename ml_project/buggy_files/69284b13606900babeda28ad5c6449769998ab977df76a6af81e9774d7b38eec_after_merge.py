    def restore(self):
        """Restore saved options from disk"""
        try:
            self.config.read(bleachbit.options_file)
        except:
            traceback.print_exc()
        if not self.config.has_section("bleachbit"):
            self.config.add_section("bleachbit")
        if not self.config.has_section("hashpath"):
            self.config.add_section("hashpath")
        if not self.config.has_section("list/shred_drives"):
            from bleachbit.FileUtilities import guess_overwrite_paths
            try:
                self.set_list('shred_drives', guess_overwrite_paths())
            except:
                traceback.print_exc()
                logger.error('error setting default shred drives')

        # set defaults
        self.__set_default("auto_hide", True)
        self.__set_default("check_beta", False)
        self.__set_default("check_online_updates", True)
        self.__set_default("shred", False)
        self.__set_default("exit_done", False)
        self.__set_default("delete_confirmation", True)
        self.__set_default("units_iec", False)

        if 'nt' == os.name:
            self.__set_default("update_winapp2", False)

        if not self.config.has_section('preserve_languages'):
            lang = bleachbit.user_locale
            pos = lang.find('_')
            if -1 != pos:
                lang = lang[0: pos]
            for _lang in set([lang, 'en']):
                logger.info("automatically preserving language '%s'", lang)
                self.set_language(_lang, True)

        # BleachBit upgrade or first start ever
        if not self.config.has_option('bleachbit', 'version') or \
                self.get('version') != bleachbit.APP_VERSION:
            self.set('first_start', True)

        # set version
        self.set("version", bleachbit.APP_VERSION)