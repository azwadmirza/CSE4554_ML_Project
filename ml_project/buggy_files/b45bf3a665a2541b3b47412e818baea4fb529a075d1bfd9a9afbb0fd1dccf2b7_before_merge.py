    def _delete_group_children_and_hosts(self):
        '''
        Clear all invalid child relationships for groups and all invalid host
        memberships.  When importing from a cloud inventory source attached to
        a specific group, only clear relationships for hosts and groups that
        are beneath the inventory source group.
        '''
        # FIXME: Optimize performance!
        if settings.SQL_DEBUG:
            queries_before = len(connection.queries)
        group_group_count = 0
        group_host_count = 0
        db_groups = self.inventory_source.groups
        # Set of all group names managed by this inventory source
        all_source_group_names = frozenset(self.all_group.all_groups.keys())
        # Set of all host pks managed by this inventory source
        all_source_host_pks = self._existing_host_pks()
        for db_group in db_groups.all():
            if self.inventory_source.deprecated_group_id == db_group.id:  # TODO: remove in 3.3
                logger.debug(
                    'Group "%s" from v1 API child group/host connections preserved',
                    db_group.name
                )
                continue
            # Delete child group relationships not present in imported data.
            db_children = db_group.children
            db_children_name_pk_map = dict(db_children.values_list('name', 'pk'))
            # Exclude child groups from removal list if they were returned by
            # the import, because this parent-child relationship has not changed
            mem_children = self.all_group.all_groups[db_group.name].children
            for mem_group in mem_children:
                db_children_name_pk_map.pop(mem_group.name, None)
            # Exclude child groups from removal list if they were not imported
            # by this specific inventory source, because
            # those relationships are outside of the dominion of this inventory source
            other_source_group_names = set(db_children_name_pk_map.keys()) - all_source_group_names
            for group_name in other_source_group_names:
                db_children_name_pk_map.pop(group_name, None)
            # Removal list is complete - now perform the removals
            del_child_group_pks = list(set(db_children_name_pk_map.values()))
            for offset in range(0, len(del_child_group_pks), self._batch_size):
                child_group_pks = del_child_group_pks[offset:(offset + self._batch_size)]
                for db_child in db_children.filter(pk__in=child_group_pks):
                    group_group_count += 1
                    db_group.children.remove(db_child)
                    logger.debug('Group "%s" removed from group "%s"',
                                 db_child.name, db_group.name)
            # FIXME: Inventory source group relationships
            # Delete group/host relationships not present in imported data.
            db_hosts = db_group.hosts
            del_host_pks = set(db_hosts.values_list('pk', flat=True))
            # Exclude child hosts from removal list if they were not imported
            # by this specific inventory source, because
            # those relationships are outside of the dominion of this inventory source
            del_host_pks = del_host_pks & all_source_host_pks
            # Exclude child hosts from removal list if they were returned by
            # the import, because this group-host relationship has not changed
            mem_hosts = self.all_group.all_groups[db_group.name].hosts
            all_mem_host_names = [h.name for h in mem_hosts if not h.instance_id]
            for offset in range(0, len(all_mem_host_names), self._batch_size):
                mem_host_names = all_mem_host_names[offset:(offset + self._batch_size)]
                for db_host_pk in db_hosts.filter(name__in=mem_host_names).values_list('pk', flat=True):
                    del_host_pks.discard(db_host_pk)
            all_mem_instance_ids = [h.instance_id for h in mem_hosts if h.instance_id]
            for offset in range(0, len(all_mem_instance_ids), self._batch_size):
                mem_instance_ids = all_mem_instance_ids[offset:(offset + self._batch_size)]
                for db_host_pk in db_hosts.filter(instance_id__in=mem_instance_ids).values_list('pk', flat=True):
                    del_host_pks.discard(db_host_pk)
            all_db_host_pks = [v for k,v in self.db_instance_id_map.items() if k in all_mem_instance_ids]
            for db_host_pk in all_db_host_pks:
                del_host_pks.discard(db_host_pk)
            # Removal list is complete - now perform the removals
            del_host_pks = list(del_host_pks)
            for offset in range(0, len(del_host_pks), self._batch_size):
                del_pks = del_host_pks[offset:(offset + self._batch_size)]
                for db_host in db_hosts.filter(pk__in=del_pks):
                    group_host_count += 1
                    if db_host not in db_group.hosts.all():
                        continue
                    db_group.hosts.remove(db_host)
                    logger.debug('Host "%s" removed from group "%s"',
                                 db_host.name, db_group.name)
        if settings.SQL_DEBUG:
            logger.warning('group-group and group-host deletions took %d queries for %d relationships',
                           len(connection.queries) - queries_before,
                           group_group_count + group_host_count)