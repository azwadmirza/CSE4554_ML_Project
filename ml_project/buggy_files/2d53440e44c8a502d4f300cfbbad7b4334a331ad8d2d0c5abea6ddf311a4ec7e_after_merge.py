    def get_all_host_objs(self, cluster_name=None, esxi_host_name=None):
        """
        Function to get all host system managed object

        Args:
            cluster_name: Name of Cluster
            esxi_host_name: Name of ESXi server

        Returns: A list of all host system managed objects, else empty list

        """
        host_obj_list = []
        if not self.is_vcenter():
            hosts = get_all_objs(self.content, [vim.HostSystem]).keys()
            if hosts:
                host_obj_list.append(list(hosts)[0])
        else:
            if cluster_name:
                cluster_obj = self.find_cluster_by_name(cluster_name=cluster_name)
                if cluster_obj:
                    host_obj_list = [host for host in cluster_obj.host]
                else:
                    self.module.fail_json(changed=False, msg="Cluster '%s' not found" % cluster_name)
            elif esxi_host_name:
                if isinstance(esxi_host_name, str):
                    esxi_host_name = [esxi_host_name]

                for host in esxi_host_name:
                    esxi_host_obj = self.find_hostsystem_by_name(host_name=host)
                    if esxi_host_obj:
                        host_obj_list = [esxi_host_obj]
                    else:
                        self.module.fail_json(changed=False, msg="ESXi '%s' not found" % host)

        return host_obj_list