    def ensure_state(self):
        """
        Manage the internal state of tags

        """
        results = dict(
            changed=False,
            tag_status=dict(),
        )
        changed = False
        action = self.params.get('state')
        available_tag_obj = self.get_tags_for_object(tag_service=self.tag_service,
                                                     tag_assoc_svc=self.tag_association_svc,
                                                     dobj=self.dynamic_managed_object)
        # Already existing tags from the given object
        avail_tag_obj_name_list = [tag.name for tag in available_tag_obj]
        results['tag_status']['previous_tags'] = avail_tag_obj_name_list
        results['tag_status']['desired_tags'] = self.tag_names

        # Check if category and tag combination exists as per user request
        removed_tags_for_set = False
        for tag in self.tag_names:
            category_obj, category_name, tag_name = None, None, None
            if ":" in tag:
                # User specified category
                category_name, tag_name = tag.split(":", 1)
                category_obj = self.search_svc_object_by_name(self.category_service, category_name)
                if not category_obj:
                    self.module.fail_json(msg="Unable to find the category %s" % category_name)
            else:
                # User specified only tag
                tag_name = tag

            tag_obj = self.search_svc_object_by_name(self.tag_service, tag_name)
            if not tag_obj:
                self.module.fail_json(msg="Unable to find the tag %s" % tag_name)

            if category_name and category_obj and not self.is_tag_category(category_obj, tag_obj):
                self.module.fail_json(msg="Category %s does not contain tag %s" % (category_name, tag_name))

            if action in ('add', 'present'):
                if tag_obj not in available_tag_obj:
                    # Tag is not already applied
                    self.tag_association_svc.attach(tag_id=tag_obj.id, object_id=self.dynamic_managed_object)
                    changed = True
            elif action == 'set':
                # Remove all tags first
                if not removed_tags_for_set:
                    for av_tag in available_tag_obj:
                        self.tag_association_svc.detach(tag_id=av_tag.id, object_id=self.dynamic_managed_object)
                    removed_tags_for_set = True
                self.tag_association_svc.attach(tag_id=tag_obj.id, object_id=self.dynamic_managed_object)
                changed = True
            elif action in ('remove', 'absent'):
                if tag_obj in available_tag_obj:
                    self.tag_association_svc.detach(tag_id=tag_obj.id, object_id=self.dynamic_managed_object)
                    changed = True

        results['tag_status']['current_tags'] = [tag.name for tag in self.get_tags_for_object(self.tag_service,
                                                                                              self.tag_association_svc,
                                                                                              self.dynamic_managed_object)]
        results['changed'] = changed
        self.module.exit_json(**results)