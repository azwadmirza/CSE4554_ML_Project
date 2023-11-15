def format_json(obj):
    result = obj.result
    input_dict = result.__dict__ if hasattr(result, '__dict__') else result
    return json.dumps(input_dict, indent=2, sort_keys=True, cls=ComplexEncoder,
                      separators=(',', ': ')) + '\n'