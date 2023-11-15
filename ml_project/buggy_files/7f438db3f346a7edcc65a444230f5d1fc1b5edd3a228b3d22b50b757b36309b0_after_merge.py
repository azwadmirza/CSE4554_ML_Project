def _process_item(item, lib, copy=False, move=False, delete=False,
                  tag=False, fmt=''):
    """Process Item `item` in `lib`.
    """
    if copy:
        item.move(basedir=copy, copy=True)
        item.store()
    if move:
        item.move(basedir=move, copy=False)
        item.store()
    if delete:
        item.remove(delete=True)
    if tag:
        try:
            k, v = tag.split('=')
        except:
            raise UserError('%s: can\'t parse k=v tag: %s' % (PLUGIN, tag))
        setattr(k, v)
        item.store()
    print_(format(item, fmt))