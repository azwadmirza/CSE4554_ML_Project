    def check_tag_status(self):
        """
        Check if tag exists or not
        Returns: 'present' if tag found, else 'absent'

        """
        ret = 'present' if self.tag_name in self.global_tags else 'absent'
        return ret