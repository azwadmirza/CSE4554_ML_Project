def prepare_framework_container_def(model, instance_type, s3_operations):
    """Prepare the framework model container information. Specify related S3
    operations for Airflow to perform. (Upload `source_dir` )

    Args:
        model (sagemaker.model.FrameworkModel): The framework model
        instance_type (str): The EC2 instance type to deploy this Model to. For
            example, 'ml.p2.xlarge'.
        s3_operations (dict): The dict to specify S3 operations (upload
            `source_dir` ).

    Returns:
        dict: The container information of this framework model.
    """
    deploy_image = model.image
    if not deploy_image:
        region_name = model.sagemaker_session.boto_session.region_name
        deploy_image = fw_utils.create_image_uri(
            region_name,
            model.__framework_name__,
            instance_type,
            model.framework_version,
            model.py_version,
        )

    base_name = utils.base_name_from_image(deploy_image)
    model.name = model.name or utils.name_from_base(base_name)

    bucket = model.bucket or model.sagemaker_session._default_bucket
    script = os.path.basename(model.entry_point)
    key = "{}/source/sourcedir.tar.gz".format(model.name)

    if model.source_dir and model.source_dir.lower().startswith("s3://"):
        code_dir = model.source_dir
        model.uploaded_code = fw_utils.UploadedCode(s3_prefix=code_dir, script_name=script)
    else:
        code_dir = "s3://{}/{}".format(bucket, key)
        model.uploaded_code = fw_utils.UploadedCode(s3_prefix=code_dir, script_name=script)
        s3_operations["S3Upload"] = [
            {"Path": model.source_dir or script, "Bucket": bucket, "Key": key, "Tar": True}
        ]

    deploy_env = dict(model.env)
    deploy_env.update(model._framework_env_vars())

    try:
        if model.model_server_workers:
            deploy_env[sagemaker.model.MODEL_SERVER_WORKERS_PARAM_NAME.upper()] = str(
                model.model_server_workers
            )
    except AttributeError:
        # This applies to a FrameworkModel which is not SageMaker Deep Learning Framework Model
        pass

    return sagemaker.container_def(deploy_image, model.model_data, deploy_env)