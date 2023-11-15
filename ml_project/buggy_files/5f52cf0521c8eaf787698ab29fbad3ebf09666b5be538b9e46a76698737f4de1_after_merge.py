    def __init__(self, base_path, home_path=Path.home(), apps=None, input_enabled=True):
        self.base_path = base_path
        self.home_path = home_path
        self.dot_briefcase_path = home_path / ".briefcase"

        self.global_config = None
        self.apps = {} if apps is None else apps
        self._path_index = {}

        # Some details about the host machine
        self.host_arch = platform.machine()
        self.host_os = platform.system()

        # External service APIs.
        # These are abstracted to enable testing without patching.
        self.cookiecutter = cookiecutter
        self.requests = requests
        self.input = Console(enabled=input_enabled)
        self.os = os
        self.sys = sys
        self.shutil = shutil
        self.subprocess = Subprocess(self)

        # The internal Briefcase integrations API.
        self.integrations = integrations