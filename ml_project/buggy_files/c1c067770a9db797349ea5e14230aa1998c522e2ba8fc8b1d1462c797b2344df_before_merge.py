    def get_objects(self):
        self.datacenter = self.find_datacenter_by_name(self.params['datacenter'])
        if not self.datacenter:
            self.module.fail_json(msg='%(datacenter)s could not be located' % self.params)

        self.datastore = None
        datastore_cluster_obj = self.find_datastore_cluster_by_name(self.params['datastore'])
        if datastore_cluster_obj:
            datastore = None
            datastore_freespace = 0
            for ds in datastore_cluster_obj.childEntity:
                if isinstance(ds, vim.Datastore) and ds.summary.freeSpace > datastore_freespace:
                    # If datastore field is provided, filter destination datastores
                    if ds.summary.maintenanceMode != 'normal' or not ds.summary.accessible:
                        continue
                    datastore = ds
                    datastore_freespace = ds.summary.freeSpace
            if datastore:
                self.datastore = datastore
        else:
            self.datastore = self.find_datastore_by_name(self.params['datastore'])

        if not self.datastore:
            self.module.fail_json(msg='%(datastore)s could not be located' % self.params)

        if self.params['cluster']:
            resource_pools = []
            cluster = self.find_cluster_by_name(self.params['cluster'], datacenter_name=self.datacenter)
            if cluster is None:
                self.module.fail_json(msg="Unable to find cluster '%(cluster)s'" % self.params)
            self.resource_pool = self.find_resource_pool_by_cluster(self.params['resource_pool'], cluster=cluster)
        else:
            self.resource_pool = self.find_resource_pool_by_name(self.params['resource_pool'])

        if not self.resource_pool:
            self.module.fail_json(msg='%(resource_pool)s could not be located' % self.params)

        for key, value in self.params['networks'].items():
            network = find_network_by_name(self.si, value)
            if not network:
                self.module.fail_json(msg='%(network)s could not be located' % self.params)
            network_mapping = vim.OvfManager.NetworkMapping()
            network_mapping.name = key
            network_mapping.network = network
            self.network_mappings.append(network_mapping)

        return self.datastore, self.datacenter, self.resource_pool, self.network_mappings