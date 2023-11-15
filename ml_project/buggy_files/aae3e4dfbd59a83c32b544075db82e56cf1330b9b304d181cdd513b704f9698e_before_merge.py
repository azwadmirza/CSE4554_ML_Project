def _create_dockerfile(output_path, mlflow_path=None):
    """
    Creates a Dockerfile containing additional Docker build steps to execute
    when building the Azure container image. These build steps perform the following tasks:

    - Install MLflow

    :param output_path: The path where the Dockerfile will be written.
    :param mlflow_path: Path to a local copy of the MLflow GitHub repository. If specified, the
                        Dockerfile command for MLflow installation will install MLflow from this
                        directory. Otherwise, it will install MLflow from pip.
    """
    docker_cmds = ["RUN pip install azureml-sdk"]

    if mlflow_path is not None:
        mlflow_install_cmd = "RUN pip install -e {mlflow_path}".format(
            mlflow_path=_get_container_path(mlflow_path))
    elif not mlflow_version.endswith("dev"):
        mlflow_install_cmd = "RUN pip install mlflow=={mlflow_version}".format(
            mlflow_version=mlflow_version)
    else:
        raise MlflowException(
                "You are running a 'dev' version of MLflow: `{mlflow_version}` that cannot be"
                " installed from pip. In order to build a container image, either specify the"
                " path to a local copy of the MLflow GitHub repository using the `mlflow_home`"
                " parameter or install a release version of MLflow from pip".format(
                    mlflow_version=mlflow_version))
    docker_cmds.append(mlflow_install_cmd)

    with open(output_path, "w") as f:
        f.write("\n".join(docker_cmds))