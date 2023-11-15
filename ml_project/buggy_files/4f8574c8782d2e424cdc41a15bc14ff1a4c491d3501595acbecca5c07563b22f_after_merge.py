    def dump(self):
        """
        Returns the string that represents the nyan file.
        """
        fileinfo_str = f"# NYAN FILE\nversion {FILE_VERSION}\n\n"
        import_str = ""
        objects_str = ""

        for nyan_object in self.nyan_objects:
            objects_str += nyan_object.dump(import_tree=self.import_tree)

        # Removes one empty newline at the end of the objects definition
        objects_str = objects_str[:-1]

        import_aliases = self.import_tree.get_import_dict()
        self.import_tree.clear_marks()

        for alias, fqon in import_aliases.items():
            import_str += "import "

            import_str += ".".join(fqon)

            import_str += f" as {alias}\n"

        import_str += "\n"

        output_str = fileinfo_str + import_str + objects_str

        return output_str