    def _create_description_match_map(
        cls,
        result_columns,
        case_sensitive=True,
        loose_column_name_matching=False,
    ):
        """when matching cursor.description to a set of names that are present
        in a Compiled object, as is the case with TextualSelect, get all the
        names we expect might match those in cursor.description.
        """

        d = {}
        for elem in result_columns:
            key = elem[RM_RENDERED_NAME]

            if not case_sensitive:
                key = key.lower()
            if key in d:
                # conflicting keyname - just add the column-linked objects
                # to the existing record.  if there is a duplicate column
                # name in the cursor description, this will allow all of those
                # objects to raise an ambiguous column error
                e_name, e_obj, e_type = d[key]
                d[key] = e_name, e_obj + elem[RM_OBJECTS], e_type
            else:
                d[key] = (elem[RM_NAME], elem[RM_OBJECTS], elem[RM_TYPE])

            if loose_column_name_matching:
                # when using a textual statement with an unordered set
                # of columns that line up, we are expecting the user
                # to be using label names in the SQL that match to the column
                # expressions.  Enable more liberal matching for this case;
                # duplicate keys that are ambiguous will be fixed later.
                for r_key in elem[RM_OBJECTS]:
                    d.setdefault(
                        r_key, (elem[RM_NAME], elem[RM_OBJECTS], elem[RM_TYPE])
                    )

        return d