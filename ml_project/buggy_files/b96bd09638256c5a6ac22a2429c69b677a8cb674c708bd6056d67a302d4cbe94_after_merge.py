def get_browsable_activities(node):
    """Get Browsable Activities"""
    try:
        browse_dic = {}
        schemes = []
        mime_types = []
        hosts = []
        ports = []
        paths = []
        path_prefixs = []
        path_patterns = []
        catg = node.getElementsByTagName("category")
        for cat in catg:
            if cat.getAttribute("android:name") == "android.intent.category.BROWSABLE":
                datas = node.getElementsByTagName("data")
                for data in datas:
                    scheme = data.getAttribute("android:scheme")
                    if scheme and scheme not in schemes:
                        schemes.append(scheme)
                    mime = data.getAttribute("android:mimeType")
                    if mime and mime not in mime_types:
                        mime_types.append(mime)
                    host = data.getAttribute("android:host")
                    if host and host not in hosts:
                        hosts.append(host)
                    port = data.getAttribute("android:port")
                    if port and port not in ports:
                        ports.append(port)
                    path = data.getAttribute("android:path")
                    if path and path not in paths:
                        paths.append(path)
                    path_prefix = data.getAttribute("android:pathPrefix")
                    if path_prefix and path_prefix not in path_prefixs:
                        path_prefixs.append(path_prefix)
                    path_pattern = data.getAttribute("android:pathPattern")
                    if path_pattern and path_pattern not in path_patterns:
                        path_patterns.append(path_pattern)
        schemes = [scheme + "://" for scheme in schemes]
        browse_dic["schemes"] = schemes
        browse_dic["mime_types"] = mime_types
        browse_dic["hosts"] = hosts
        browse_dic["ports"] = ports
        browse_dic["paths"] = paths
        browse_dic["path_prefixs"] = path_prefixs
        browse_dic["path_patterns"] = path_patterns
        browse_dic["browsable"] = bool(browse_dic["schemes"])
        return browse_dic
    except:
        PrintException("Getting Browsable Activities")