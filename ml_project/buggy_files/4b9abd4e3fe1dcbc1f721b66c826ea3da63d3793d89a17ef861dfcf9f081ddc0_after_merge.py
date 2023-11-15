    def state_delete_tag(self):
        """
        Delete tag

        """
        tag_id = self.global_tags[self.tag_name]['tag_id']
        try:
            self.tag_service.delete(tag_id=tag_id)
        except Error as error:
            self.module.fail_json(msg="%s" % self.get_error_message(error))
        self.module.exit_json(changed=True,
                              results=dict(msg="Tag '%s' deleted." % self.tag_name,
                                           tag_id=tag_id))