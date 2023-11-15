    def check_row(self, cells):
        row_number = cells[0]['row-number']

        # Prepare keyed_row
        keyed_row = {}
        for cell in cells:
            if cell.get('field'):
                keyed_row[cell.get('field').name] = cell.get('value')

        # Resolve relations
        errors = []
        for foreign_key in self.__schema.foreign_keys:
            success = _resolve_relations(
                deepcopy(keyed_row), self.__foreign_keys_values, foreign_key)
            if success is None:
                message = 'Foreign key "{fields}" violation in row {row_number}'
                message_substitutions = {'fields': foreign_key['fields']}

                # if not a composite foreign-key, add the cell causing the violation to improve the error details
                # with the column-number
                error_cell = None
                if len(foreign_key['fields']) == 1:
                    for cell in cells:
                        if cell['header'] == foreign_key['fields'][0]:
                            error_cell = cell
                            break

                errors.append(Error(
                    self.__code,
                    cell=error_cell,
                    row_number=row_number,
                    message=message,
                    message_substitutions=message_substitutions,
                ))

        return errors