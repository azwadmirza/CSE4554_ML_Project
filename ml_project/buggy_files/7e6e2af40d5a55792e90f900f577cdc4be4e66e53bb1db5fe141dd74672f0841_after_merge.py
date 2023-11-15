def print_result_line(result, schema_name, index, total):
    node = result.node

    if node.get('resource_type') == NodeType.Model:
        print_model_result_line(result, schema_name, index, total)
    elif node.get('resource_type') == NodeType.Test:
        print_test_result_line(result, schema_name, index, total)
    elif node.get('resource_type') == NodeType.Archive:
        print_archive_result_line(result, index, total)