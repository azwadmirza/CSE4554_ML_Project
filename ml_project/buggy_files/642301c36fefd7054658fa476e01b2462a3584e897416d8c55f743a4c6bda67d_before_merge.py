    def _generate_path(self, path, attr, wildcard_key, raiseerr=True):
        self._of_type = None

        if raiseerr and not path.has_entity:
            if isinstance(path, TokenRegistry):
                raise sa_exc.ArgumentError(
                    "Wildcard token cannot be followed by another entity")
            else:
                raise sa_exc.ArgumentError(
                    "Attribute '%s' of entity '%s' does not "
                    "refer to a mapped entity" %
                    (path.prop.key, path.parent.entity)
                )

        if isinstance(attr, util.string_types):
            default_token = attr.endswith(_DEFAULT_TOKEN)
            if attr.endswith(_WILDCARD_TOKEN) or default_token:
                if default_token:
                    self.propagate_to_loaders = False
                if wildcard_key:
                    attr = "%s:%s" % (wildcard_key, attr)
                path = path.token(attr)
                self.path = path
                return path

            try:
                # use getattr on the class to work around
                # synonyms, hybrids, etc.
                attr = getattr(path.entity.class_, attr)
            except AttributeError:
                if raiseerr:
                    raise sa_exc.ArgumentError(
                        "Can't find property named '%s' on the "
                        "mapped entity %s in this Query. " % (
                            attr, path.entity)
                    )
                else:
                    return None
            else:
                attr = attr.property

            path = path[attr]
        elif _is_mapped_class(attr):
            if not attr.common_parent(path.mapper):
                if raiseerr:
                    raise sa_exc.ArgumentError(
                        "Attribute '%s' does not "
                        "link from element '%s'" % (attr, path.entity))
                else:
                    return None
        else:
            prop = attr.property

            if not prop.parent.common_parent(path.mapper):
                if raiseerr:
                    raise sa_exc.ArgumentError(
                        "Attribute '%s' does not "
                        "link from element '%s'" % (attr, path.entity))
                else:
                    return None

            if getattr(attr, '_of_type', None):
                ac = attr._of_type
                ext_info = of_type_info = inspect(ac)

                existing = path.entity_path[prop].get(
                    self.context, "path_with_polymorphic")
                if not ext_info.is_aliased_class:
                    ac = orm_util.with_polymorphic(
                        ext_info.mapper.base_mapper,
                        ext_info.mapper, aliased=True,
                        _use_mapper_path=True,
                        _existing_alias=existing)
                    ext_info = inspect(ac)
                elif not ext_info.with_polymorphic_mappers:
                    ext_info = orm_util.AliasedInsp(
                        ext_info.entity,
                        ext_info.mapper.base_mapper,
                        ext_info.selectable,
                        ext_info.name,
                        ext_info.with_polymorphic_mappers or [ext_info.mapper],
                        ext_info.polymorphic_on,
                        ext_info._base_alias,
                        ext_info._use_mapper_path,
                        ext_info._adapt_on_names,
                        ext_info.represents_outer_join
                    )

                path.entity_path[prop].set(
                    self.context, "path_with_polymorphic", ext_info)

                # the path here will go into the context dictionary and
                # needs to match up to how the class graph is traversed.
                # so we can't put an AliasedInsp in the path here, needs
                # to be the base mapper.
                path = path[prop][ext_info.mapper]

                # but, we need to know what the original of_type()
                # argument is for cache key purposes.  so....store that too.
                # it might be better for "path" to really represent,
                # "the path", but trying to keep the impact of the cache
                # key feature localized for now
                self._of_type = of_type_info
            else:
                path = path[prop]

        if path.has_entity:
            path = path.entity_path
        self.path = path
        return path