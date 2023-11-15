def __execute_cmd(name, xml):
    '''
    Execute ilom commands
    '''
    ret = {name.replace('_', ' '): {}}
    id_num = 0

    tmp_dir = os.path.join(__opts__['cachedir'], 'tmp')
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)
    with tempfile.NamedTemporaryFile(dir=tmp_dir,
                                     prefix=name+str(os.getpid()),
                                     suffix='.xml',
                                     delete=False) as fh:
        tmpfilename = fh.name
        fh.write(xml)

    cmd = __salt__['cmd.run_all']('hponcfg -f {0}'.format(tmpfilename))

    # Clean up the temp file
    __salt__['file.remove'](tmpfilename)

    if cmd['retcode'] != 0:
        for i in cmd['stderr'].splitlines():
            if i.startswith('     MESSAGE='):
                return {'Failed': i.split('=')[-1]}
        return False

    try:
        for i in ET.fromstring(''.join(cmd['stdout'].splitlines()[3:-1])):
            # Make sure dict keys dont collide
            if ret[name.replace('_', ' ')].get(i.tag, False):
                ret[name.replace('_', ' ')].update(
                    {i.tag + '_' + str(id_num): i.attrib}
                )
                id_num += 1
            else:
                ret[name.replace('_', ' ')].update(
                    {i.tag: i.attrib}
                )
    except SyntaxError:
        return True

    return ret