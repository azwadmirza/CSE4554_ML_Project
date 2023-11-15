def batch_predict(project_id, model_path, input_paths, input_data_format, 
    output_path, region, job_id_output_path, output_data_format=None, prediction_input=None, job_id_prefix=None,
    wait_interval=30):
    """Creates a MLEngine batch prediction job.

    Args:
        project_id (str): Required. The ID of the parent project of the job.
        model_path (str): Required. The path to the model. It can be either:
            `projects/[PROJECT_ID]/models/[MODEL_ID]` or 
            `projects/[PROJECT_ID]/models/[MODEL_ID]/versions/[VERSION_ID]`
            or a GCS path of a model file.
        input_paths (list): Required. The Google Cloud Storage location of 
            the input data files. May contain wildcards.
        input_data_format (str): Required. The format of the input data files.
            See https://cloud.google.com/ml-engine/reference/rest/v1/projects.jobs#DataFormat.
        output_path (str): Required. The output Google Cloud Storage location.
        region (str): Required. The Google Compute Engine region to run the 
            prediction job in.
        output_data_format (str): Optional. Format of the output data files, 
            defaults to JSON.
        prediction_input (dict): Input parameters to create a prediction job.
        job_id_prefix (str): the prefix of the generated job id.
        wait_interval (int): optional wait interval between calls
            to get job status. Defaults to 30.
    """
    if not prediction_input:
        prediction_input = {}
    if not model_path:
        raise ValueError('model_path must be provided.')
    if _is_model_name(model_path):
        prediction_input['modelName'] = model_path
    elif _is_model_version_name(model_path):
        prediction_input['versionName'] = model_path
    elif _is_gcs_path(model_path):
        prediction_input['uri'] = model_path
    else:
        raise ValueError('model_path value is invalid.')
    
    if input_paths:
        prediction_input['inputPaths'] = input_paths
    if input_data_format:
        prediction_input['dataFormat'] = input_data_format
    if output_path:
        prediction_input['outputPath'] = output_path
    if output_data_format:
        prediction_input['outputDataFormat'] = output_data_format
    if region:
        prediction_input['region'] = region
    job = {
        'predictionInput': prediction_input
    }
    create_job(project_id, job, job_id_prefix, wait_interval, job_id_output_path=job_id_output_path)