    def set_manager_attributes(self, attr):
        result = {}
        # Here I'm making the assumption that the key 'Attributes' is part of the URI.
        # It may not, but in the hardware I tested with, getting to the final URI where
        # the Manager Attributes are, appear to be part of a specific OEM extension.
        key = "Attributes"

        # Search for key entry and extract URI from it
        response = self.get_request(self.root_uri + self.manager_uri + "/" + key)
        if response['ret'] is False:
            return response
        result['ret'] = True
        data = response['data']

        if key not in data:
            return {'ret': False, 'msg': "Key %s not found" % key}

        # Check if attribute exists
        if attr['mgr_attr_name'] not in data[key]:
            return {'ret': False, 'msg': "Manager attribute %s not found" % attr['mgr_attr_name']}

        # Example: manager_attr = {\"name\":\"value\"}
        # Check if value is a number. If so, convert to int.
        if attr['mgr_attr_value'].isdigit():
            manager_attr = "{\"%s\": %i}" % (attr['mgr_attr_name'], int(attr['mgr_attr_value']))
        else:
            manager_attr = "{\"%s\": \"%s\"}" % (attr['mgr_attr_name'], attr['mgr_attr_value'])

        # Find out if value is already set to what we want. If yes, return
        if data[key][attr['mgr_attr_name']] == attr['mgr_attr_value']:
            return {'ret': True, 'changed': False, 'msg': "Manager attribute already set"}

        payload = {"Attributes": json.loads(manager_attr)}
        response = self.patch_request(self.root_uri + self.manager_uri + "/" + key, payload, HEADERS)
        if response['ret'] is False:
            return response
        return {'ret': True, 'changed': True, 'msg': "Modified Manager attribute %s" % attr['mgr_attr_name']}