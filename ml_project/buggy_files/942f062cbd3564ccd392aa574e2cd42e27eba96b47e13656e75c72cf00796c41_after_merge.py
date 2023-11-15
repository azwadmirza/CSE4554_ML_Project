def generate_admin_dict(array):
    api_version = array._list_available_rest_versions()
    admin_facts = {}
    if ADMIN_API_VERSION in api_version:
        admins = array.list_admins()
        for admin in range(0, len(admins)):
            admin_name = admins[admin]['name']
            admin_facts[admin_name] = {
                'type': admins[admin]['type'],
                'role': admins[admin]['role'],
            }
    return admin_facts