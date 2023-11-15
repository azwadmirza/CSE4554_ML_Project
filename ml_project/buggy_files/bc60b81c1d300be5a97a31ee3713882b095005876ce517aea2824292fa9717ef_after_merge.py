def create_version(model_name, deployemnt_uri=None, version_id=None, 
    runtime_version=None, python_version=None, version=None, 
    replace_existing=False, wait_interval=30,
    version_name_output_path='/tmp/kfp/output/ml_engine/version_name.txt',
    version_object_output_path='/tmp/kfp/output/ml_engine/version.json',
):
    """Creates a MLEngine version and wait for the operation to be done.

    Args:
        model_name (str): required, the name of the parent model.
        deployment_uri (str): optional, the Google Cloud Storage location of 
            the trained model used to create the version.
        version_id (str): optional, the user provided short name of 
            the version. If it is not provided, the operation uses a random name.
        runtime_version (str): optinal, the Cloud ML Engine runtime version 
            to use for this deployment. If not set, Cloud ML Engine uses 
            the default stable version, 1.0. 
        python_version (str): optinal, the version of Python used in prediction. 
            If not set, the default version is '2.7'. Python '3.5' is available
            when runtimeVersion is set to '1.4' and above. Python '2.7' works 
            with all supported runtime versions.
        version (dict): optional, the payload of the new version.
        replace_existing (boolean): boolean flag indicates whether to replace 
            existing version in case of conflict.
        wait_interval (int): the interval to wait for a long running operation.
    """
    if not version:
        version = {}
    if deployemnt_uri:
        version['deploymentUri'] = deployemnt_uri
    if version_id:
        version['name'] = version_id
    if runtime_version:
        version['runtimeVersion'] = runtime_version
    if python_version:
        version['pythonVersion'] = python_version

    return CreateVersionOp(model_name, version, 
        replace_existing, wait_interval,
        version_name_output_path=version_name_output_path,
        version_object_output_path=version_object_output_path,
    ).execute_and_wait()