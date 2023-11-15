    def __init__(self, config_file, tool_source, app, guid=None, repository_id=None, allow_code_files=True):
        """Load a tool from the config named by `config_file`"""
        # Determine the full path of the directory where the tool config is
        self.config_file = config_file
        self.tool_dir = os.path.dirname(config_file)
        self.app = app
        self.repository_id = repository_id
        self._allow_code_files = allow_code_files
        # setup initial attribute values
        self.inputs = odict()
        self.stdio_exit_codes = list()
        self.stdio_regexes = list()
        self.inputs_by_page = list()
        self.display_by_page = list()
        self.action = '/tool_runner/index'
        self.target = 'galaxy_main'
        self.method = 'post'
        self.labels = []
        self.check_values = True
        self.nginx_upload = False
        self.input_required = False
        self.display_interface = True
        self.require_login = False
        self.rerun = False
        # Define a place to keep track of all input   These
        # differ from the inputs dictionary in that inputs can be page
        # elements like conditionals, but input_params are basic form
        # parameters like SelectField objects.  This enables us to more
        # easily ensure that parameter dependencies like index files or
        # tool_data_table_conf.xml entries exist.
        self.input_params = []
        # Attributes of tools installed from Galaxy tool sheds.
        self.tool_shed = None
        self.repository_name = None
        self.repository_owner = None
        self.changeset_revision = None
        self.installed_changeset_revision = None
        self.sharable_url = None
        # The tool.id value will be the value of guid, but we'll keep the
        # guid attribute since it is useful to have.
        self.guid = guid
        self.old_id = None
        self.version = None
        self._lineage = None
        self.dependencies = []
        # populate toolshed repository info, if available
        self.populate_tool_shed_info()
        # add tool resource parameters
        self.populate_resource_parameters(tool_source)
        # Parse XML element containing configuration
        try:
            self.parse(tool_source, guid=guid)
        except Exception as e:
            global_tool_errors.add_error(config_file, "Tool Loading", e)
            raise e
        # The job search is only relevant in a galaxy context, and breaks
        # loading tools into the toolshed for validation.
        if self.app.name == 'galaxy':
            self.job_search = JobSearch(app=self.app)