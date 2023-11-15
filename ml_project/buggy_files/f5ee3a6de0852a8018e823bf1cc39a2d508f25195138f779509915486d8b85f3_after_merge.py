    def _describe_type(self, t, view_shapes, view_shapes_metadata,
                       follow_links: bool = True):
        # The encoding format is documented in edb/api/types.txt.

        buf = self.buffer

        if isinstance(t, s_types.Tuple):
            subtypes = [self._describe_type(st, view_shapes,
                                            view_shapes_metadata)
                        for st in t.get_subtypes(self.schema)]

            if t.is_named(self.schema):
                element_names = list(t.get_element_names(self.schema))
                assert len(element_names) == len(subtypes)

                type_id = self._get_collection_type_id(
                    t.schema_name, subtypes, element_names)

                if type_id in self.uuid_to_pos:
                    return type_id

                buf.append(CTYPE_NAMEDTUPLE)
                buf.append(type_id.bytes)
                buf.append(_uint16_packer(len(subtypes)))
                for el_name, el_type in zip(element_names, subtypes):
                    el_name_bytes = el_name.encode('utf-8')
                    buf.append(_uint32_packer(len(el_name_bytes)))
                    buf.append(el_name_bytes)
                    buf.append(_uint16_packer(self.uuid_to_pos[el_type]))

            else:
                type_id = self._get_collection_type_id(t.schema_name, subtypes)

                if type_id in self.uuid_to_pos:
                    return type_id

                buf.append(CTYPE_TUPLE)
                buf.append(type_id.bytes)
                buf.append(_uint16_packer(len(subtypes)))
                for el_type in subtypes:
                    buf.append(_uint16_packer(self.uuid_to_pos[el_type]))

            self._register_type_id(type_id)
            return type_id

        elif isinstance(t, s_types.Array):
            subtypes = [self._describe_type(st, view_shapes,
                                            view_shapes_metadata)
                        for st in t.get_subtypes(self.schema)]

            assert len(subtypes) == 1
            type_id = self._get_collection_type_id(t.schema_name, subtypes)

            if type_id in self.uuid_to_pos:
                return type_id

            buf.append(CTYPE_ARRAY)
            buf.append(type_id.bytes)
            buf.append(_uint16_packer(self.uuid_to_pos[subtypes[0]]))
            # Number of dimensions (currently always 1)
            buf.append(_uint16_packer(1))
            # Dimension cardinality (currently always unbound)
            buf.append(_int32_packer(-1))

            self._register_type_id(type_id)
            return type_id

        elif isinstance(t, s_types.Collection):
            raise errors.SchemaError(f'unsupported collection type {t!r}')

        elif view_shapes.get(t):
            # This is a view
            self.schema, mt = t.material_type(self.schema)
            base_type_id = mt.id

            subtypes = []
            element_names = []
            link_props = []
            links = []

            metadata = view_shapes_metadata.get(t)
            implicit_id = metadata is not None and metadata.has_implicit_id

            for ptr in view_shapes[t]:
                if ptr.singular(self.schema):
                    if isinstance(ptr, s_links.Link) and not follow_links:
                        subtype_id = self._describe_type(
                            self.schema.get('std::uuid'), view_shapes,
                            view_shapes_metadata,
                        )
                    else:
                        subtype_id = self._describe_type(
                            ptr.get_target(self.schema), view_shapes,
                            view_shapes_metadata)
                else:
                    if isinstance(ptr, s_links.Link) and not follow_links:
                        raise errors.InternalServerError(
                            'cannot describe multi links when '
                            'follow_links=False'
                        )
                    else:
                        subtype_id = self._describe_set(
                            ptr.get_target(self.schema), view_shapes,
                            view_shapes_metadata)
                subtypes.append(subtype_id)
                element_names.append(ptr.get_shortname(self.schema).name)
                link_props.append(False)
                links.append(not ptr.is_property(self.schema))

            t_rptr = t.get_rptr(self.schema)
            if t_rptr is not None and (rptr_ptrs := view_shapes.get(t_rptr)):
                # There are link properties in the mix
                for ptr in rptr_ptrs:
                    if ptr.singular(self.schema):
                        subtype_id = self._describe_type(
                            ptr.get_target(self.schema), view_shapes,
                            view_shapes_metadata)
                    else:
                        subtype_id = self._describe_set(
                            ptr.get_target(self.schema), view_shapes,
                            view_shapes_metadata)
                    subtypes.append(subtype_id)
                    element_names.append(
                        ptr.get_shortname(self.schema).name)
                    link_props.append(True)
                    links.append(False)

            type_id = self._get_object_type_id(
                base_type_id, subtypes, element_names,
                links_props=link_props, links=links,
                has_implicit_fields=implicit_id)

            if type_id in self.uuid_to_pos:
                return type_id

            buf.append(CTYPE_SHAPE)
            buf.append(type_id.bytes)

            assert len(subtypes) == len(element_names)
            buf.append(_uint16_packer(len(subtypes)))

            for el_name, el_type, el_lp, el_l in zip(element_names,
                                                     subtypes, link_props,
                                                     links):
                flags = 0
                if el_lp:
                    flags |= self.EDGE_POINTER_IS_LINKPROP
                if (implicit_id and el_name == 'id') or el_name == '__tid__':
                    if el_type != UUID_TYPE_ID:
                        raise errors.InternalServerError(
                            f"{el_name!r} is expected to be a 'std::uuid' "
                            f"singleton")
                    flags |= self.EDGE_POINTER_IS_IMPLICIT
                if el_l:
                    flags |= self.EDGE_POINTER_IS_LINK
                buf.append(_uint8_packer(flags))

                el_name_bytes = el_name.encode('utf-8')
                buf.append(_uint32_packer(len(el_name_bytes)))
                buf.append(el_name_bytes)
                buf.append(_uint16_packer(self.uuid_to_pos[el_type]))

            self._register_type_id(type_id)
            return type_id

        elif isinstance(t, s_scalars.ScalarType):
            # This is a scalar type

            self.schema, mt = t.material_type(self.schema)
            type_id = mt.id
            if type_id in self.uuid_to_pos:
                # already described
                return type_id

            base_type = mt.get_topmost_concrete_base(self.schema)
            enum_values = mt.get_enum_values(self.schema)

            if enum_values:
                buf.append(CTYPE_ENUM)
                buf.append(type_id.bytes)
                buf.append(_uint16_packer(len(enum_values)))
                for enum_val in enum_values:
                    enum_val_bytes = enum_val.encode('utf-8')
                    buf.append(_uint32_packer(len(enum_val_bytes)))
                    buf.append(enum_val_bytes)

            elif mt is base_type:
                buf.append(CTYPE_BASE_SCALAR)
                buf.append(type_id.bytes)

            else:
                bt_id = self._describe_type(
                    base_type, view_shapes, view_shapes_metadata)

                buf.append(CTYPE_SCALAR)
                buf.append(type_id.bytes)
                buf.append(_uint16_packer(self.uuid_to_pos[bt_id]))

            self._register_type_id(type_id)
            return type_id

        else:
            raise errors.InternalServerError(
                f'cannot describe type {t.get_name(self.schema)}')