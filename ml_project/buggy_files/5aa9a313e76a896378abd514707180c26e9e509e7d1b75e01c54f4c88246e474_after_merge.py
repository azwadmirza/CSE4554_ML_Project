    def get_objects_permissions(self, objects_ids, permissions=None):
        query = """
        WITH required_object_ids AS (
          VALUES %(objects_ids)s
        )
        SELECT object_id, permission, principal
            FROM required_object_ids JOIN access_control_entries
              ON (object_id = column2)
              %(permissions_condition)s
        ORDER BY column1 ASC;
        """
        obj_ids_values = ','.join(["(%s, '%s')" % t
                                   for t in enumerate(objects_ids)])
        safeholders = {
            'objects_ids': obj_ids_values,
            'permissions_condition': ''
        }
        placeholders = {}
        if permissions is not None:
            safeholders['permissions_condition'] = """
              WHERE permission IN :permissions"""
            placeholders["permissions"] = tuple(permissions)

        with self.client.connect(readonly=True) as conn:
            result = conn.execute(query % safeholders, placeholders)
            rows = result.fetchall()

        groupby_id = OrderedDict()
        for object_id in objects_ids:
            groupby_id[object_id] = {}
        for row in rows:
            object_id, permission, principal = (row['object_id'],
                                                row['permission'],
                                                row['principal'])
            groupby_id[object_id].setdefault(permission, set()).add(principal)
        return list(groupby_id.values())