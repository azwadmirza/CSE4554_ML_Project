    def __init__(self, module):
        super(HostVmnicMgr, self).__init__(module)
        self.capabilities = self.params.get('capabilities')
        self.directpath_io = self.params.get('directpath_io')
        self.sriov = self.params.get('sriov')
        cluster_name = self.params.get('cluster_name', None)
        esxi_host_name = self.params.get('esxi_hostname', None)
        self.hosts = self.get_all_host_objs(cluster_name=cluster_name, esxi_host_name=esxi_host_name)
        if not self.hosts:
            self.module.fail_json(msg="Failed to find host system.")