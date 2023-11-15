def generate_admin_dict(array):
    admin_facts = {}
    admins = array.list_admins()
    for admin in range(0, len(admins)):
        admin_name = admins[admin]['name']
        admin_facts[admin_name] = {
            'type': admins[admin]['type'],
            'role': admins[admin]['role'],
        }
    return admin_facts