    def get_app_kwds(cls, config_section, app_name=None):
        kwds = {
            'config_file': None,
            'config_section': config_section,
        }
        uwsgi_opt = uwsgi.opt
        config_file = None
        # check for --set galaxy_config_file=<path>, this overrides whatever config file uWSGI was loaded with (which
        # may not actually include a Galaxy config)
        if uwsgi_opt.get("galaxy_config_file"):
            config_file = uwsgi_opt.get("galaxy_config_file")
        # check for --yaml or --json uWSGI config options next
        if config_file is None:
            config_file = (UWSGIApplicationStack._get_config_file(uwsgi_opt.get("yaml"), yaml.safe_load, config_section)
                           or UWSGIApplicationStack._get_config_file(uwsgi_opt.get("json"), json.load, config_section))
        # --ini and --ini-paste don't behave the same way, but this method will only be called by mules if the main
        # application was loaded with --ini-paste, so we can make some assumptions, most notably, uWSGI does not have
        # any way to set the app name when loading with paste.deploy:loadapp(), so hardcoding the alternate section
        # name to `app:main` is fine.
        has_ini_config = config_file is None and uwsgi_opt.get("ini") or uwsgi_opt.get("ini-paste")
        has_ini_config = has_ini_config or (config_file and has_ext(config_file, "ini", aliases=True, ignore="sample"))
        if has_ini_config:
            config_file = config_file or uwsgi_opt.get("ini") or uwsgi_opt.get("ini-paste")
            parser = nice_config_parser(config_file)
            if not parser.has_section(config_section) and parser.has_section('app:main'):
                kwds['config_section'] = 'app:main'
        kwds['config_file'] = config_file
        return kwds