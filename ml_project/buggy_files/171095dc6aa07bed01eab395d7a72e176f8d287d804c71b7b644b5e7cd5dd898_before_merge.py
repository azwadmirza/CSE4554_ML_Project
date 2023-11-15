    def organize_nyan_objects(modpack, full_data_set):
        """
        Put available nyan objects into a given modpack.
        """
        created_nyan_files = {}

        # Access all raw API objects
        raw_api_objects = []
        raw_api_objects.extend(full_data_set.pregen_nyan_objects.values())

        for unit_line in full_data_set.unit_lines.values():
            raw_api_objects.extend(unit_line.get_raw_api_objects().values())

        for building_line in full_data_set.building_lines.values():
            raw_api_objects.extend(building_line.get_raw_api_objects().values())

        for ambient_group in full_data_set.ambient_groups.values():
            raw_api_objects.extend(ambient_group.get_raw_api_objects().values())

        for variant_group in full_data_set.variant_groups.values():
            raw_api_objects.extend(variant_group.get_raw_api_objects().values())

        for tech_group in full_data_set.tech_groups.values():
            raw_api_objects.extend(tech_group.get_raw_api_objects().values())

        for terrain_group in full_data_set.terrain_groups.values():
            raw_api_objects.extend(terrain_group.get_raw_api_objects().values())

        for civ_group in full_data_set.civ_groups.values():
            raw_api_objects.extend(civ_group.get_raw_api_objects().values())

        # Create the files
        for raw_api_object in raw_api_objects:
            obj_location = raw_api_object.get_location()

            if isinstance(obj_location, ForwardRef):
                # Resolve location and add nested object
                nyan_object = obj_location.resolve()
                nyan_object.add_nested_object(raw_api_object.get_nyan_object())
                continue

            obj_filename = raw_api_object.get_filename()
            nyan_file_path = f"{modpack.info.name}/{obj_location}{obj_filename}"

            if nyan_file_path in created_nyan_files.keys():
                nyan_file = created_nyan_files[nyan_file_path]

            else:
                nyan_file = NyanFile(obj_location, obj_filename,
                                     modpack.info.name)
                created_nyan_files.update({nyan_file.get_relative_file_path(): nyan_file})
                modpack.add_data_export(nyan_file)

            nyan_file.add_nyan_object(raw_api_object.get_nyan_object())

        # Create an import tree from the files
        import_tree = ImportTree()

        for nyan_file in created_nyan_files.values():
            import_tree.expand_from_file(nyan_file)

        for nyan_object in full_data_set.nyan_api_objects.values():
            import_tree.expand_from_object(nyan_object)

        for nyan_file in created_nyan_files.values():
            nyan_file.set_import_tree(import_tree)