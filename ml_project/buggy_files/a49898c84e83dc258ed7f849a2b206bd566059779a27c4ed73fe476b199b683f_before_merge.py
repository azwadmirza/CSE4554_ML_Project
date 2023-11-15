    def __init__(self, service, project, dataset, prefix=""):
        self.__service = service
        self.__project = project
        self.__dataset = dataset
        self.__prefix = prefix
        self.__names = None
        self.__tables = {}
        self.__fallbacks = {}