    def _set_field_values(self, values_map: Dict[str, Any]) -> Set[str]:
        """
        Sets values for fields honoring type transformations and
        return list of fields that were set additionally
        """
        meta = self._meta
        passed_fields = set()

        for key, value in values_map.items():
            if key in meta.fk_fields:
                if not getattr(value, "_saved_in_db", False):
                    raise OperationalError(
                        "You should first call .save() on {} before referring to it".format(value)
                    )
                field_object = meta.fields_map[key]
                relation_field = field_object.source_field  # type: str  # type: ignore
                setattr(self, relation_field, value.pk)
                passed_fields.add(relation_field)
            elif key in meta.fields:
                field_object = meta.fields_map[key]
                if value is None and not field_object.null:
                    raise ValueError("{} is non nullable field, but null was passed".format(key))
                setattr(self, key, field_object.to_python_value(value))
            elif key in meta.db_fields:
                field_object = meta.fields_map[meta.fields_db_projection_reverse[key]]
                if value is None and not field_object.null:
                    raise ValueError("{} is non nullable field, but null was passed".format(key))
                setattr(self, key, field_object.to_python_value(value))
            elif key in meta.backward_fk_fields:
                raise ConfigurationError(
                    "You can't set backward relations through init, change related model instead"
                )
            elif key in meta.m2m_fields:
                raise ConfigurationError(
                    "You can't set m2m relations through init, use m2m_manager instead"
                )

        return passed_fields