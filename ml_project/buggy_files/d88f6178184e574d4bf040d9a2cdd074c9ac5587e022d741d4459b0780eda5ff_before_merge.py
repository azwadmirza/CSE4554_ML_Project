    def _delete_hosts(self):
        '''
        For each host in the database that is NOT in the local list, delete
        it. When importing from a cloud inventory source attached to a
        specific group, only delete hosts beneath that group.  Delete each
        host individually so signal handlers will run.
        '''
        if settings.SQL_DEBUG:
            queries_before = len(connection.queries)
        hosts_qs = self.inventory_source.hosts
        # Build list of all host pks, remove all that should not be deleted.
        del_host_pks = set(hosts_qs.values_list('pk', flat=True))
        if self.instance_id_var:
            all_instance_ids = self.mem_instance_id_map.keys()
            instance_ids = []
            for offset in range(0, len(all_instance_ids), self._batch_size):
                instance_ids = all_instance_ids[offset:(offset + self._batch_size)]
                for host_pk in hosts_qs.filter(instance_id__in=instance_ids).values_list('pk', flat=True):
                    del_host_pks.discard(host_pk)
            for host_pk in set([v for k,v in self.db_instance_id_map.items() if k in instance_ids]):
                del_host_pks.discard(host_pk)
            all_host_names = list(set(self.mem_instance_id_map.values()) - set(self.all_group.all_hosts.keys()))
        else:
            all_host_names = list(self.all_group.all_hosts.keys())
        for offset in range(0, len(all_host_names), self._batch_size):
            host_names = all_host_names[offset:(offset + self._batch_size)]
            for host_pk in hosts_qs.filter(name__in=host_names).values_list('pk', flat=True):
                del_host_pks.discard(host_pk)
        # Now delete all remaining hosts in batches.
        all_del_pks = sorted(list(del_host_pks))
        for offset in range(0, len(all_del_pks), self._batch_size):
            del_pks = all_del_pks[offset:(offset + self._batch_size)]
            for host in hosts_qs.filter(pk__in=del_pks):
                host_name = host.name
                host.delete()
                logger.debug('Deleted host "%s"', host_name)
        if settings.SQL_DEBUG:
            logger.warning('host deletions took %d queries for %d hosts',
                           len(connection.queries) - queries_before,
                           len(all_del_pks))