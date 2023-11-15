    def _delete_groups(self):
        '''
        # If overwrite is set, for each group in the database that is NOT in
        # the local list, delete it. When importing from a cloud inventory
        # source attached to a specific group, only delete children of that
        # group.  Delete each group individually so signal handlers will run.
        '''
        if settings.SQL_DEBUG:
            queries_before = len(connection.queries)
        groups_qs = self.inventory_source.groups.all()
        # Build list of all group pks, remove those that should not be deleted.
        del_group_pks = set(groups_qs.values_list('pk', flat=True))
        all_group_names = list(self.all_group.all_groups.keys())
        for offset in range(0, len(all_group_names), self._batch_size):
            group_names = all_group_names[offset:(offset + self._batch_size)]
            for group_pk in groups_qs.filter(name__in=group_names).values_list('pk', flat=True):
                del_group_pks.discard(group_pk)
        if self.inventory_source.deprecated_group_id in del_group_pks:  # TODO: remove in 3.3
            logger.warning(
                'Group "%s" from v1 API is not deleted by overwrite',
                self.inventory_source.deprecated_group.name
            )
            del_group_pks.discard(self.inventory_source.deprecated_group_id)
        # Now delete all remaining groups in batches.
        all_del_pks = sorted(list(del_group_pks))
        for offset in range(0, len(all_del_pks), self._batch_size):
            del_pks = all_del_pks[offset:(offset + self._batch_size)]
            for group in groups_qs.filter(pk__in=del_pks):
                group_name = group.name
                with ignore_inventory_computed_fields():
                    group.delete()
                logger.debug('Group "%s" deleted', group_name)
        if settings.SQL_DEBUG:
            logger.warning('group deletions took %d queries for %d groups',
                           len(connection.queries) - queries_before,
                           len(all_del_pks))