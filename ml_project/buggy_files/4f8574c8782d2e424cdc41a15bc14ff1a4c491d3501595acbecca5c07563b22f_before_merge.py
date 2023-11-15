    def dump(self):
        """
        Returns the string that represents the nyan file.
        """
        output_str = f"# NYAN FILE\nversion {FILE_VERSION}\n\n"

        import_aliases = self.import_tree.establish_import_dict(self,
                                                                ignore_names=["type", "types"])

        for alias, fqon in import_aliases.items():
            output_str += "import "

            output_str += ".".join(fqon)

            output_str += f" as {alias}\n"

        output_str += "\n"

        for nyan_object in self.nyan_objects:
            output_str += nyan_object.dump(import_tree=self.import_tree)

        self.import_tree.clear_marks()

        # Removes one empty line at the end of the file
        output_str = output_str[:-1]

        return output_str