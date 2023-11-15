    def generate_http_access_url(self, file_path):
        # e.g., file_path is like this format: [datastore0] test_vm/test_vm-1.png
        # from file_path generate URL
        url_path = None
        if not file_path:
            return url_path

        path = "/folder/%s" % quote(file_path.split()[1])
        params = dict(dsName=file_path.split()[0].strip('[]'))
        if not self.is_vcenter():
            datacenter = 'ha-datacenter'
        else:
            if self.params.get('datacenter'):
                datacenter = self.params['datacenter']
            else:
                datacenter = self.get_parent_datacenter(self.current_vm_obj).name
            datacenter = datacenter.replace('&', '%26')
        params['dcPath'] = datacenter
        url_path = "https://%s%s?%s" % (self.params['hostname'], path, urlencode(params))

        return url_path