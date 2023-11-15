    def set_manager_attributes(self, attr):
        attributes = "Attributes"

        # Example: manager_attr = {\"name\":\"value\"}
        # Check if value is a number. If so, convert to int.
        if attr['mgr_attr_value'].isdigit():
            manager_attr = "{\"%s\": %i}" % (attr['mgr_attr_name'], int(attr['mgr_attr_value']))
        else:
            manager_attr = "{\"%s\": \"%s\"}" % (attr['mgr_attr_name'], attr['mgr_attr_value'])

        payload = {"Attributes": json.loads(manager_attr)}
        response = self.patch_request(self.root_uri + self.manager_uri + "/" + attributes, payload, HEADERS)
        if response['ret'] is False:
            return response
        return {'ret': True}