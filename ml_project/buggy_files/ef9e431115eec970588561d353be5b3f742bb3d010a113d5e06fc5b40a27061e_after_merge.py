def sync_list_repositories_grpc(api_client):
    from dagster.grpc.client import DagsterGrpcClient
    from dagster.grpc.types import ListRepositoriesResponse

    check.inst_param(api_client, 'api_client', DagsterGrpcClient)
    result = check.inst(
        api_client.list_repositories(), (ListRepositoriesResponse, SerializableErrorInfo)
    )
    if isinstance(result, SerializableErrorInfo):
        raise DagsterUserCodeProcessError(
            result.to_string(), user_code_process_error_infos=[result]
        )
    else:
        return result