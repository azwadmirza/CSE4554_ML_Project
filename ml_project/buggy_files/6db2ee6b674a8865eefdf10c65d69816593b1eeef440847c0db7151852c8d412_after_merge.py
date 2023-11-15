    def _group_references_by_file(self, references: 'List[ReferenceDict]'
                                  ) -> 'Dict[str, List[Tuple[Point, str]]]':
        """ Return a dictionary that groups references by the file it belongs. """
        grouped_references = {}  # type: Dict[str, List[Tuple[Point, str]]]
        for reference in references:
            file_path = uri_to_filename(reference["uri"])
            point = Point.from_lsp(reference['range']['start'])

            # get line of the reference, to showcase its use
            reference_line = linecache.getline(file_path, point.row + 1).strip()

            if grouped_references.get(file_path) is None:
                grouped_references[file_path] = []
            grouped_references[file_path].append((point, reference_line))

        # we don't want to cache the line, we always want to get fresh data
        linecache.clearcache()

        return grouped_references