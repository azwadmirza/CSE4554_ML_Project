    def _get_transform_args(self, desc, inputs, name, volume_kms_key):
        """Format training args to pass in sagemaker_session.train.

        Args:
            desc (dict): the response from DescribeTrainingJob API.
            inputs (str): an S3 uri where new input dataset is stored.
            name (str): the name of the step job.
            volume_kms_key (str): The KMS key id to encrypt data on the storage volume attached to
                the ML compute instance(s).

        Returns (dcit): a dictionary that can be used as args of
            sagemaker_session.transform method.
        """
        transform_args = {}
        transform_args["job_name"] = name
        transform_args["model_name"] = desc["ModelName"]
        transform_args["output_config"] = desc["TransformOutput"]
        transform_args["resource_config"] = desc["TransformResources"]
        transform_args["data_processing"] = desc["DataProcessing"]
        transform_args["tags"] = []
        transform_args["strategy"] = None
        transform_args["max_concurrent_transforms"] = None
        transform_args["max_payload"] = None
        transform_args["env"] = None

        input_config = desc["TransformInput"]
        input_config["DataSource"]["S3DataSource"]["S3Uri"] = inputs
        transform_args["input_config"] = input_config

        if volume_kms_key is not None:
            transform_args["resource_config"]["VolumeKmsKeyId"] = volume_kms_key
        if "BatchStrategy" in desc:
            transform_args["strategy"] = desc["BatchStrategy"]
        if "MaxConcurrentTransforms" in desc:
            transform_args["max_concurrent_transforms"] = desc["MaxConcurrentTransforms"]
        if "MaxPayloadInMB" in desc:
            transform_args["max_payload"] = desc["MaxPayloadInMB"]
        if "Environment" in desc:
            transform_args["env"] = desc["Environment"]

        return transform_args