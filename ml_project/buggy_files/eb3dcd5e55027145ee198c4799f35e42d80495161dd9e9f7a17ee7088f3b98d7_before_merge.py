def generate_operation_id(*, route: routing.APIRoute, method: str) -> str:
    if route.operation_id:
        return route.operation_id
    path: str = route.path_format
    operation_id = route.name + path
    operation_id = operation_id.replace("{", "_").replace("}", "_").replace("/", "_")
    operation_id = operation_id + "_" + method.lower()
    return operation_id