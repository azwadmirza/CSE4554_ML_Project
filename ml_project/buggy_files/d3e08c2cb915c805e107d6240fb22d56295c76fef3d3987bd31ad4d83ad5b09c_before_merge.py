    def delete_map(self, query=None):
        query_map = self.interpolated_map(query=query)
        for alias, drivers in query_map.copy().items():
            for driver, vms in drivers.copy().items():
                for vm_name, vm_details in vms.copy().items():
                    if vm_details == "Absent":
                        query_map[alias][driver].pop(vm_name)
                if not query_map[alias][driver]:
                    query_map[alias].pop(driver)
            if not query_map[alias]:
                query_map.pop(alias)
        return query_map