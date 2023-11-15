    def _generate_path(
        self,
        path,
        attr,
        for_strategy,
        wildcard_key,
        raiseerr=True,
        polymorphic_entity_context=None,
    ):
        existing_of_type = self._of_type
        self._of_type = None
        if raiseerr and not path.has_entity:
            if isinstance(path, TokenRegistry):
                raise sa_exc.ArgumentError(
                    "Wildcard token cannot be followed by another entity"
                )
            else:
                raise sa_exc.ArgumentError(
                    "Mapped attribute '%s' does not "
                    "refer to a mapped entity" % (path.prop,)
                )

        if isinstance(attr, util.string_types):
            default_token = attr.endswith(_DEFAULT_TOKEN)
            if attr.endswith(_WILDCARD_TOKEN) or default_token:
                if default_token:
                    self.propagate_to_loaders = False
                if wildcard_key:
                    attr = "%s:%s" % (wildcard_key, attr)

                # TODO: AliasedInsp inside the path for of_type is not
                # working for a with_polymorphic entity because the
                # relationship loaders don't render the with_poly into the
                # path.  See #4469 which will try to improve this
                if existing_of_type and not existing_of_type.is_aliased_class:
                    path = path.parent[existing_of_type]
                path = path.token(attr)
                self.path = path
                return path

            if existing_of_type:
                ent = inspect(existing_of_type)
            else:
                ent = path.entity

            try:
                # use getattr on the class to work around
                # synonyms, hybrids, etc.
                attr = getattr(ent.class_, attr)
            except AttributeError as err:
                if raiseerr:
                    util.raise_(
                        sa_exc.ArgumentError(
                            'Can\'t find property named "%s" on '
                            "%s in this Query." % (attr, ent)
                        ),
                        replace_context=err,
                    )
                else:
                    return None
            else:
                attr = found_property = attr.property

            path = path[attr]
        elif _is_mapped_class(attr):
            # TODO: this does not appear to be a valid codepath.  "attr"
            # would never be a mapper.  This block is present in 1.2
            # as well however does not seem to be accessed in any tests.
            if not orm_util._entity_corresponds_to_use_path_impl(
                attr.parent, path[-1]
            ):
                if raiseerr:
                    raise sa_exc.ArgumentError(
                        "Attribute '%s' does not "
                        "link from element '%s'" % (attr, path.entity)
                    )
                else:
                    return None
        else:
            prop = found_property = attr.property

            if not orm_util._entity_corresponds_to_use_path_impl(
                attr.parent, path[-1]
            ):
                if raiseerr:
                    raise sa_exc.ArgumentError(
                        'Attribute "%s" does not '
                        'link from element "%s".%s'
                        % (
                            attr,
                            path.entity,
                            (
                                "  Did you mean to use "
                                "%s.of_type(%s)?"
                                % (path[-2], attr.class_.__name__)
                                if len(path) > 1
                                and path.entity.is_mapper
                                and attr.parent.is_aliased_class
                                else ""
                            ),
                        )
                    )
                else:
                    return None

            if attr._extra_criteria:
                self._extra_criteria = attr._extra_criteria

            if getattr(attr, "_of_type", None):
                ac = attr._of_type
                ext_info = of_type_info = inspect(ac)

                if polymorphic_entity_context is None:
                    polymorphic_entity_context = self.context

                existing = path.entity_path[prop].get(
                    polymorphic_entity_context, "path_with_polymorphic"
                )

                if not ext_info.is_aliased_class:
                    ac = orm_util.with_polymorphic(
                        ext_info.mapper.base_mapper,
                        ext_info.mapper,
                        aliased=True,
                        _use_mapper_path=True,
                        _existing_alias=inspect(existing)
                        if existing is not None
                        else None,
                    )

                    ext_info = inspect(ac)

                path.entity_path[prop].set(
                    polymorphic_entity_context, "path_with_polymorphic", ac
                )

                path = path[prop][ext_info]

                self._of_type = of_type_info

            else:
                path = path[prop]

        if for_strategy is not None:
            found_property._get_strategy(for_strategy)
        if path.has_entity:
            path = path.entity_path
        self.path = path
        return path