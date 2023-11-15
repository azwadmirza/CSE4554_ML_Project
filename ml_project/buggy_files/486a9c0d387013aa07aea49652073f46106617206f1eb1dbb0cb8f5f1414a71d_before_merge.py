    def __init__(self):
        super(CPPStandaloneDevice, self).__init__()
        #: Dictionary mapping `ArrayVariable` objects to their globally
        #: unique name
        self.arrays = {}
        #: Dictionary mapping `ArrayVariable` objects to their value or to
        #: ``None`` if the value (potentially) depends on executed code. This
        #: mechanism allows to access state variables in standalone mode if
        #: their value is known at run time
        self.array_cache = {}
        #: List of all dynamic arrays
        #: Dictionary mapping `DynamicArrayVariable` objects with 1 dimension to
        #: their globally unique name
        self.dynamic_arrays = {}
        #: Dictionary mapping `DynamicArrayVariable` objects with 2 dimensions
        #: to their globally unique name
        self.dynamic_arrays_2d = {}
        #: List of all arrays to be filled with zeros (list of (var, varname) )
        self.zero_arrays = []
        #: List of all arrays to be filled with numbers (list of
        #: (var, varname, start) tuples
        self.arange_arrays = []

        #: Whether the simulation has been run
        self.has_been_run = False

        #: Whether a run should trigger a build
        self.build_on_run = False

        #: build options
        self.build_options = None

        #: The directory which contains the generated code and results
        self.project_dir = None

        #: Whether to generate profiling information (stored in an instance
        #: variable to be accessible during CodeObject generation)
        self.enable_profiling = False

        #: CodeObjects that use profiling (users can potentially enable
        #: profiling only for a subset of runs)
        self.profiled_codeobjects = []

        #: Dict of all static saved arrays
        self.static_arrays = {}

        self.code_objects = {}
        self.main_queue = []
        self.runfuncs = {}
        self.networks = []
        self.net_synapses = [] 
        self.static_array_specs =[]
        self.report_func = ''
        self.synapses = []

        #: Code lines that have been manually added with `device.insert_code`
        #: Dictionary mapping slot names to lists of lines.
        #: Note that the main slot is handled separately as part of `main_queue`
        self.code_lines = {'before_start': [],
                           'after_start': [],
                           'before_end': [],
                           'after_end': []}

        self.clocks = set([])

        self.extra_compile_args = []
        self.define_macros = []
        self.headers = []
        self.include_dirs = ['brianlib/randomkit']
        if sys.platform == 'win32':
            self.include_dirs += [os.path.join(sys.prefix, 'Library', 'include')]
        else:
            self.include_dirs += [os.path.join(sys.prefix, 'include')]
        self.library_dirs = ['brianlib/randomkit']
        if sys.platform == 'win32':
            self.library_dirs += [os.path.join(sys.prefix, 'Library', 'Lib')]
        else:
            self.library_dirs += [os.path.join(sys.prefix, 'lib')]
        self.runtime_library_dirs = []
        if sys.platform.startswith('linux'):
            self.runtime_library_dirs += [os.path.join(sys.prefix, 'lib')]
        self.run_environment_variables = {}
        if sys.platform.startswith('darwin'):
            if 'DYLD_LIBRARY_PATH' in os.environ:
                dyld_library_path = (os.environ['DYLD_LIBRARY_PATH'] + ':' +
                                     os.path.join(sys.prefix, 'lib'))
            else:
                dyld_library_path = os.path.join(sys.prefix, 'lib')
            self.run_environment_variables['DYLD_LIBRARY_PATH'] = dyld_library_path
        self.libraries = []
        if sys.platform == 'win32':
            self.libraries += ['advapi32']
        self.extra_link_args = []
        self.writer = None