def get_lang_from_content(src_path):
    # NODE: package.json should exist in the application root dir
    # NETCORE & DOTNET: *.csproj should exist in the application dir
    # NETCORE: <TargetFramework>netcoreapp2.0</TargetFramework>
    # DOTNET: <TargetFrameworkVersion>v4.5.2</TargetFrameworkVersion>
    runtime_details_dict = dict.fromkeys(['language', 'file_loc', 'default_sku'])
    package_json_file = os.path.join(src_path, 'package.json')
    package_python_file = os.path.join(src_path, 'requirements.txt')
    package_netcore_file = ""
    static_html_file = ""

    import fnmatch
    for _dirpath, _dirnames, files in os.walk(src_path):
        for file in files:
            if fnmatch.fnmatch(file, "*.csproj"):
                package_netcore_file = os.path.join(src_path, file)
                break
            if fnmatch.fnmatch(file, "*.html"):
                static_html_file = os.path.join(src_path, file)
                break

    if os.path.isfile(package_python_file):
        runtime_details_dict['language'] = PYTHON_RUNTIME_NAME
        runtime_details_dict['file_loc'] = package_python_file
        runtime_details_dict['default_sku'] = LINUX_SKU_DEFAULT
    elif os.path.isfile(package_json_file) or os.path.isfile('server.js') or os.path.isfile('index.js'):
        runtime_details_dict['language'] = NODE_RUNTIME_NAME
        runtime_details_dict['file_loc'] = package_json_file if os.path.isfile(package_json_file) else ''
        runtime_details_dict['default_sku'] = LINUX_SKU_DEFAULT
    elif package_netcore_file:
        runtime_lang = detect_dotnet_lang(package_netcore_file)
        runtime_details_dict['language'] = runtime_lang
        runtime_details_dict['file_loc'] = package_netcore_file
        runtime_details_dict['default_sku'] = 'F1'
    elif static_html_file:
        runtime_details_dict['language'] = STATIC_RUNTIME_NAME
        runtime_details_dict['file_loc'] = static_html_file
        runtime_details_dict['default_sku'] = 'F1'
    return runtime_details_dict