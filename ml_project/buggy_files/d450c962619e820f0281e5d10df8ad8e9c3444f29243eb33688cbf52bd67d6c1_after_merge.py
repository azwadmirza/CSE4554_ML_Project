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

        _temp_prev_tags = ["%s:%s" % (tag['category_name'], tag['name']) for tag in self.get_tags_for_dynamic_obj(mid=self.dynamic_managed_object)]
        results['tag_status']['previous_tags'] = _temp_prev_tags
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

            if category_name:
                tag_obj = self.get_tag_by_category(tag_name=tag_name, category_name=category_name)
            else:
                tag_obj = self.get_tag_by_name(tag_name=tag_name)

            if not tag_obj:
                self.module.fail_json(msg="Unable to find the tag %s" % tag_name)

            if action in ('add', 'present'):
                if tag_obj not in available_tag_obj:
                    # Tag is not already applied
                    try:
                        self.tag_association_svc.attach(tag_id=tag_obj.id, object_id=self.dynamic_managed_object)
                        changed = True
                    except Error as error:
                        self.module.fail_json(msg="%s" % self.get_error_message(error))

            elif action == 'set':
                # Remove all tags first
                try:
                    if not removed_tags_for_set:
                        for av_tag in available_tag_obj:
                            self.tag_association_svc.detach(tag_id=av_tag.id, object_id=self.dynamic_managed_object)
                        removed_tags_for_set = True
                    self.tag_association_svc.attach(tag_id=tag_obj.id, object_id=self.dynamic_managed_object)
                    changed = True
                except Error as error:
                    self.module.fail_json(msg="%s" % self.get_error_message(error))

            elif action in ('remove', 'absent'):
                if tag_obj in available_tag_obj:
                    try:
                        self.tag_association_svc.detach(tag_id=tag_obj.id, object_id=self.dynamic_managed_object)
                        changed = True
                    except Error as error:
                        self.module.fail_json(msg="%s" % self.get_error_message(error))

        _temp_curr_tags = ["%s:%s" % (tag['category_name'], tag['name']) for tag in self.get_tags_for_dynamic_obj(mid=self.dynamic_managed_object)]
        results['tag_status']['current_tags'] = _temp_curr_tags
        results['changed'] = changed
        self.module.exit_json(**results)