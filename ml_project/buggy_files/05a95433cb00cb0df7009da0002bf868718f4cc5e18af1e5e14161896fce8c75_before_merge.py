    def read_metadata(self, post, file_metadata_regexp=None, unslugify_titles=False, lang=None):
        """Read metadata directly from ipynb file.

        As ipynb file support arbitrary metadata as json, the metadata used by Nikola
        will be assume to be in the 'nikola' subfield.
        """
        if flag is None:
            req_missing(['ipython[notebook]>=2.0.0'], 'build this site (compile ipynb)')
        source = post.source_path
        with io.open(source, "r", encoding="utf8") as in_file:
            nb_json = nbformat.read(in_file, current_nbformat)
        # Metadata might not exist in two-file posts or in hand-crafted
        # .ipynb files.
        return nb_json.get('metadata', {}).get('nikola', {})