def print_start_line(node, schema_name, index, total):
    if node.get('resource_type') == NodeType.Model:
        print_model_start_line(node, schema_name, index, total)
    if node.get('resource_type') == NodeType.Test:
        print_test_start_line(node, schema_name, index, total)