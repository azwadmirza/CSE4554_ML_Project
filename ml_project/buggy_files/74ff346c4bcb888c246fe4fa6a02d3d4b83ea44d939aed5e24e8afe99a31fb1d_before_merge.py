def missing_header(cells, sample):
    errors = []

    for cell in copy(cells):

        # Skip if header in cell
        if cell.get('header') is not None:
            continue

        # Add error
        message_substitutions = {
            'field_name': '"{}"'.format(cell['field'].name),
        }
        error = Error(
            'missing-header',
            cell,
            message_substitutions=message_substitutions
        )
        errors.append(error)

        # Remove cell
        cells.remove(cell)

    return errors