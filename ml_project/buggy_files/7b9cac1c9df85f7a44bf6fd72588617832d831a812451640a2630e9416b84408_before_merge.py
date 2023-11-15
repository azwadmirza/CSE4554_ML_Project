    def _find_section_header(self, line: Text) -> Optional[Tuple[Text, Text]]:
        """Checks if the current line contains a section header
        and returns the section and the title."""
        match = re.search(r"##\s*(.+):(.+)", line)
        if match is not None:
            return match.group(1), match.group(2)

        return None