def do_batch_update(cursor: CursorObj,
                    table: str,
                    cols: List[str],
                    vals: List[str],
                    batch_size: int=10000,
                    sleep: float=0.1,
                    escape: bool=True) -> None:  # nocoverage
    stmt = '''
        UPDATE %s
        SET (%s) = ROW(%s)
        WHERE id >= %%s AND id < %%s
    ''' % (table, ', '.join(cols), ', '.join(['%s'] * len(cols)))

    cursor.execute("SELECT MIN(id), MAX(id) FROM %s" % (table,))
    (min_id, max_id) = cursor.fetchall()[0]
    if min_id is None:
        return

    print("\n    Range of rows to update: [%s, %s]" % (min_id, max_id))
    while min_id <= max_id:
        lower = min_id
        upper = min_id + batch_size
        print('    Updating range [%s,%s)' % (lower, upper))
        params = list(vals) + [lower, upper]
        if escape:
            cursor.execute(stmt, params=params)
        else:
            cursor.execute(stmt % tuple(params))

        min_id = upper
        time.sleep(sleep)

        # Once we've finished, check if any new rows were inserted to the table
        if min_id > max_id:
            cursor.execute("SELECT MAX(id) FROM %s" % (table,))
            max_id = cursor.fetchall()[0][0]

    print("    Finishing...", end='')