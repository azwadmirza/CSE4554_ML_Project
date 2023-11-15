def get_os_version_info():
    info = OSVERSIONINFOEX()
    ret = {'MajorVersion': info.dwMajorVersion,
           'MinorVersion': info.dwMinorVersion,
           'BuildNumber': info.dwBuildNumber,
           'PlatformID': info.dwPlatformId,
           'ServicePackMajor': info.wServicePackMajor,
           'ServicePackMinor': info.wServicePackMinor,
           'SuiteMask': info.wSuiteMask,
           'ProductType': info.wProductType}

    return ret