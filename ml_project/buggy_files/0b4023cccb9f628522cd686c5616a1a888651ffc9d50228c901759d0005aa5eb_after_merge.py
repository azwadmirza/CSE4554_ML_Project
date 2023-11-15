def info(name):
    '''
    .. versionadded:: 2015.8.4

    Return the gluster volume info.

    name
        Volume name

    CLI Example:

    .. code-block:: bash

        salt '*' glusterfs.info myvolume

    '''
    cmd = 'volume info {0}'.format(name)
    root = _gluster_xml(cmd)

    volume = [x for x in _iter(root, 'volume')][0]

    ret = {name: _etree_to_dict(volume)}

    bricks = {}
    for i, brick in enumerate(_iter(volume, 'brick'), start=1):
        brickkey = 'brick{0}'.format(i)
        bricks[brickkey] = {'path': brick.text}
        for child in list(brick):
            if not child.tag == 'name':
                bricks[brickkey].update({child.tag: child.text})
        for k, v in brick.items():
            bricks[brickkey][k] = v
    ret[name]['bricks'] = bricks

    options = {}
    for option in _iter(volume, 'option'):
        options[option.find('name').text] = option.find('value').text
    ret[name]['options'] = options

    return ret