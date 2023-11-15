    def create(
        self,
        entity=None,
        result_state=None,
        fail_condition=lambda e: False,
        search_params=None,
        update_params=None,
        _wait=None,
        **kwargs
    ):
        """
        Method which is called when state of the entity is 'present'. If user
        don't provide `entity` parameter the entity is searched using
        `search_params` parameter. If entity is found it's updated, whether
        the entity should be updated is checked by `update_check` method.
        The corresponding updated entity is build by `build_entity` method.

        Function executed after entity is created can optionally be specified
        in `post_create` parameter. Function executed after entity is updated
        can optionally be specified in `post_update` parameter.

        :param entity: Entity we want to update, if exists.
        :param result_state: State which should entity has in order to finish task.
        :param fail_condition: Function which checks incorrect state of entity, if it returns `True` Exception is raised.
        :param search_params: Dictionary of parameters to be used for search.
        :param update_params: The params which should be passed to update method.
        :param kwargs: Additional parameters passed when creating entity.
        :return: Dictionary with values returned by Ansible module.
        """
        if entity is None:
            entity = self.search_entity(search_params)

        self.pre_create(entity)

        if entity:
            # Entity exists, so update it:
            entity_service = self._service.service(entity.id)
            if not self.update_check(entity):
                new_entity = self.build_entity()
                if not self._module.check_mode:
                    update_params = update_params or {}
                    updated_entity = entity_service.update(
                        new_entity,
                        **update_params
                    )
                    self.post_update(entity)

                # Update diffs only if user specified --diff parameter,
                # so we don't useless overload API:
                if self._module._diff:
                    before = get_dict_of_struct(
                        entity,
                        self._connection,
                        fetch_nested=True,
                        attributes=['name'],
                    )
                    after = before.copy()
                    self.diff_update(after, get_dict_of_struct(new_entity))
                    self._diff['before'] = before
                    self._diff['after'] = after

                self.changed = True
        else:
            # Entity don't exists, so create it:
            if not self._module.check_mode:
                entity = self._service.add(
                    self.build_entity(),
                    **kwargs
                )
                self.post_create(entity)
            self.changed = True

        if not self._module.check_mode:
            # Wait for the entity to be created and to be in the defined state:
            entity_service = self._service.service(entity.id)

            def state_condition(entity):
                return entity

            if result_state:

                def state_condition(entity):
                    return entity and entity.status == result_state

            wait(
                service=entity_service,
                condition=state_condition,
                fail_condition=fail_condition,
                wait=_wait if _wait is not None else self._module.params['wait'],
                timeout=self._module.params['timeout'],
                poll_interval=self._module.params['poll_interval'],
            )

        return {
            'changed': self.changed,
            'id': getattr(entity, 'id', None),
            type(entity).__name__.lower(): get_dict_of_struct(
                struct=entity,
                connection=self._connection,
                fetch_nested=self._module.params.get('fetch_nested'),
                attributes=self._module.params.get('nested_attributes'),
            ),
            'diff': self._diff,
        }