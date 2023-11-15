    def storage_get_data(self, node_dict):
        local_storage = {'knots': [], 'knotsnames': []}

        for knot in self.SvLists['knots'].SvSubLists:
            local_storage['knots'].append([knot.SvX, knot.SvY, knot.SvZ])

        for outname in self.SvLists['knotsnames'].SvSubLists:
            local_storage['knotsnames'].append(outname.SvName)
        
        node_dict['profile_sublist_storage'] = json.dumps(local_storage, sort_keys=True)
        node_dict['path_file'] = bpy.data.texts[self.filename].as_string()