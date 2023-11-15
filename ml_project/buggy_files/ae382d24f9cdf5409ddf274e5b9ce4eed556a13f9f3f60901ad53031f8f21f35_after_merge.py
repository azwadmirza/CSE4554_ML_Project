    def check_tag_status(self):
        """
        Check if tag exists or not
        Returns: 'present' if tag found, else 'absent'

        """
        if 'category_id' in self.params:
            if self.tag_name in self.global_tags and self.params['category_id'] == self.global_tags[self.tag_name]['tag_category_id']:
                ret = 'present'
            else:
                ret = 'absent'
        else:
            ret = 'present' if self.tag_name in self.global_tags else 'absent'
        return ret