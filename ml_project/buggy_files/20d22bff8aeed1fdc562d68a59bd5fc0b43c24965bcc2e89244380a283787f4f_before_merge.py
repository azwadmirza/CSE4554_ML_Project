def _prepare_serial_port_xml(serial_type='pty', telnet_port='', console=True, **kwargs_sink):
    '''
    Prepares the serial and console sections of the VM xml

    serial_type: presently 'pty' or 'tcp'(telnet)

    telnet_port: When selecting tcp, which port to listen on

    console: Is this serial device the console or for some other purpose

    Returns string representing the serial and console devices suitable for
    insertion into the VM XML definition
    '''
    fn_ = 'serial_port_{0}.jinja'.format(serial_type)
    try:
        template = JINJA.get_template(fn_)
    except jinja2.exceptions.TemplateNotFound:
        log.error('Could not load template {0}'.format(fn_))
        return ''
    return template.render(serial_type=serial_type,
                           telnet_port=telnet_port,
                           console=console)