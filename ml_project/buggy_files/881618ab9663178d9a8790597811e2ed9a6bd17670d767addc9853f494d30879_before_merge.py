    def __init__(self, param_dict, bucket_name, region, boto_client, az_excludes=None):
        self.regxfind = CommonTools.regxfind
        self._param_dict = param_dict
        self.results = {}
        self.mutated_params = {}
        self.param_name = None
        self.param_value = None
        self.bucket_name = bucket_name
        self._boto_client = boto_client
        self.region = region
        if not az_excludes:
            self.az_excludes: Set[str] = set()
        else:
            self.az_excludes: Set[str] = az_excludes
        self.transform_parameter()