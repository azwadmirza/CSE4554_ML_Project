def get_context_from_analysis_ios(app_dict, info_dict,code_dict, files, sfiles):
    """Get the context for IOS ZIP from analysis results"""
    try:
        context = {
            'title': 'Static Analysis',
            'file_name': app_dict["file_name"],
            'size': app_dict["size"],
            'md5': app_dict["md5_hash"],
            'sha1': app_dict["sha1"],
            'sha256': app_dict["sha256"],
            'plist': info_dict["plist_xml"],
            'bin_name': info_dict["bin_name"],
            'id': info_dict["id"],
            'build': info_dict["bundle_version_name"],
            'version': info_dict['bundle_version_name'],
            'sdk': info_dict["sdk"],
            'pltfm': info_dict["pltfm"],
            'min': info_dict["min"],
            'files': files,
            'file_analysis': sfiles,
            'api': code_dict["api"],
            'insecure': code_dict["code_anal"],
            'urls': code_dict["urlnfile"],
            'domains': code_dict["domains"],
            'emails': code_dict["emailnfile"],
            'permissions': info_dict["permissions"],
            'insecure_connections': info_dict["inseccon"],
            'bundle_name': info_dict["bundle_name"],
            'bundle_url_types': info_dict["bundle_url_types"],
            'bundle_supported_platforms': info_dict["bundle_supported_platforms"],
            'bundle_localizations': info_dict["bundle_localizations"],
        }
        return context
    except:
        PrintException("Rendering to Template")