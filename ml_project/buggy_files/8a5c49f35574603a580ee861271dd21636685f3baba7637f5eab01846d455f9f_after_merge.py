    def __init__(
        self,
        expectation_suite_name,
        expectations=None,
        evaluation_parameters=None,
        data_asset_type=None,
        meta=None,
    ):
        self.expectation_suite_name = expectation_suite_name
        if expectations is None:
            expectations = []
        self.expectations = [
            ExpectationConfiguration(**expectation)
            if isinstance(expectation, dict)
            else expectation
            for expectation in expectations
        ]
        if evaluation_parameters is None:
            evaluation_parameters = {}
        self.evaluation_parameters = evaluation_parameters
        self.data_asset_type = data_asset_type
        if meta is None:
            meta = {"great_expectations.__version__": ge_version}
        if not "great_expectations.__version__" in meta.keys():
            meta["great_expectations.__version__"] = ge_version
        # We require meta information to be serializable, but do not convert until necessary
        ensure_json_serializable(meta)
        self.meta = meta