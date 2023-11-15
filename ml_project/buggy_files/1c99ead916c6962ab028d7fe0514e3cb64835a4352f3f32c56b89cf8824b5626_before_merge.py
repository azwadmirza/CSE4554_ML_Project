    def __init__(self,
                 module_dirs,
                 opts=None,
                 tag='module',
                 loaded_base_name=None,
                 mod_type_check=None,
                 pack=None,
                 whitelist=None,
                 virtual_enable=True,
                 static_modules=None
                 ):  # pylint: disable=W0231

        self.inject_globals = {}
        self.opts = self.__prep_mod_opts(opts)

        self.module_dirs = module_dirs
        if opts is None:
            opts = {}
        self.tag = tag
        self.loaded_base_name = loaded_base_name or LOADED_BASE_NAME
        self.mod_type_check = mod_type_check or _mod_type

        self.pack = {} if pack is None else pack
        if '__context__' not in self.pack:
            self.pack['__context__'] = {}

        self.whitelist = whitelist
        self.virtual_enable = virtual_enable
        self.initial_load = True

        # names of modules that we don't have (errors, __virtual__, etc.)
        self.missing_modules = {}  # mapping of name -> error
        self.loaded_modules = {}  # mapping of module_name -> dict_of_functions
        self.loaded_files = set()  # TODO: just remove them from file_mapping?
        self.static_modules = static_modules if static_modules else []

        self.disabled = set(self.opts.get('disable_{0}s'.format(self.tag), []))

        self.refresh_file_mapping()

        super(LazyLoader, self).__init__()  # late init the lazy loader
        # create all of the import namespaces
        _generate_module('{0}.int'.format(self.loaded_base_name))
        _generate_module('{0}.int.{1}'.format(self.loaded_base_name, tag))
        _generate_module('{0}.ext'.format(self.loaded_base_name))
        _generate_module('{0}.ext.{1}'.format(self.loaded_base_name, tag))