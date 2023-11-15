    def __init__(self, plugin_class, module_path, parent):
        super().__init__()
        self.__deps: Dict[str, str] = {}
        self.__cfls: Dict[str, str] = {}
        self.__plugins: Dict[str, Union[AppletPlugin, ManagerPlugin]] = {}
        self.__classes: Dict[str, Type[Union[AppletPlugin, ManagerPlugin]]] = {}
        self.__loaded: List[str] = []
        self.parent = parent

        self.module_path = module_path
        self.plugin_class = plugin_class