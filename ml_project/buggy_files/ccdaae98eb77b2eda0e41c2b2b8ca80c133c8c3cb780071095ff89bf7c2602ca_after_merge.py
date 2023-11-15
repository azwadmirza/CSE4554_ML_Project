    def __init__(self,
                 api_key: Optional[str] = None,
                 project_name: Optional[str] = None,
                 close_after_fit: Optional[bool] = True,
                 offline_mode: bool = False,
                 experiment_name: Optional[str] = None,
                 upload_source_files: Optional[List[str]] = None,
                 params: Optional[Dict[str, Any]] = None,
                 properties: Optional[Dict[str, Any]] = None,
                 tags: Optional[List[str]] = None,
                 **kwargs):
        super().__init__()
        self.api_key = api_key
        self.project_name = project_name
        self.offline_mode = offline_mode
        self.close_after_fit = close_after_fit
        self.experiment_name = experiment_name
        self.upload_source_files = upload_source_files
        self.params = params
        self.properties = properties
        self.tags = tags
        self._kwargs = kwargs
        self._experiment_id = None
        self._experiment = self._create_or_get_experiment()

        log.info(f'NeptuneLogger will work in {"offline" if self.offline_mode else "online"} mode')