def process_set(hive, hive_name, key, flags, default_arch):
    try:
        with winreg.OpenKeyEx(hive, key, access=winreg.KEY_READ | flags) as root_key:
            for company in enum_keys(root_key):
                if company == "PyLauncher":  # reserved
                    continue
                for spec in process_company(hive_name, company, root_key, default_arch):
                    yield spec
    except OSError:
        pass