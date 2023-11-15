def list_cache_contents(cmd):
    from glob import glob
    directory = _get_cache_directory(cmd.cli_ctx)
    contents = []
    rg_paths = glob(os.path.join(directory, '*'))
    for rg_path in rg_paths:
        rg_name = os.path.split(rg_path)[1]
        for dir_name, _, file_list in os.walk(rg_path):
            if not file_list:
                continue
            resource_type = os.path.split(dir_name)[1]
            for f in file_list:
                with open(os.path.join(dir_name, f), 'r') as cache_file:
                    cache_obj = json.loads(cache_file.read())
                contents.append({
                    'resourceGroup': rg_name,
                    'resourceType': resource_type,
                    'name': f.split('.', 1)[0],
                    'lastTouched': cache_obj['_last_touched'],
                })
    return contents