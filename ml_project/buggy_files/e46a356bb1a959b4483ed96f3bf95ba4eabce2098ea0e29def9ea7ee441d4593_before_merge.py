    def _create_tag(self, tag_str):
        """Create a Tag object from a tag string."""
        tag_hierarchy = tag_str.split(self.hierarchy_separator)
        tag_prefix = ""
        parent_tag = None
        for sub_tag in tag_hierarchy:
            # Get or create subtag.
            tag_name = tag_prefix + self._scrub_tag_name(sub_tag)
            tag = self._get_tag(tag_name)
            if not tag:
                tag = self._create_tag_instance(tag_name)
            # Set tag parent.
            tag.parent = parent_tag
            # Update parent and tag prefix.
            parent_tag = tag
            tag_prefix = tag.name + self.hierarchy_separator
        return tag