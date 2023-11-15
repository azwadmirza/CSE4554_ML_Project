def _generate_minion_id():
    '''
    Get list of possible host names and convention names.

    :return:
    '''
    # There are three types of hostnames:
    # 1. Network names. How host is accessed from the network.
    # 2. Host aliases. They might be not available in all the network or only locally (/etc/hosts)
    # 3. Convention names, an internal nodename.

    class DistinctList(list):
        '''
        List, which allows one to append only distinct objects.
        Needs to work on Python 2.6, because of collections.OrderedDict only since 2.7 version.
        Override 'filter()' for custom filtering.
        '''
        localhost_matchers = [r'localhost.*', r'ip6-.*', r'127[.]\d', r'0\.0\.0\.0',
                              r'::1.*', r'ipv6-.*', r'fe00::.*', r'fe02::.*', r'1.0.0.*.ip6.arpa']

        def append(self, p_object):
            if p_object and p_object not in self and not self.filter(p_object):
                super(self.__class__, self).append(p_object)
            return self

        def extend(self, iterable):
            for obj in iterable:
                self.append(obj)
            return self

        def filter(self, element):
            'Returns True if element needs to be filtered'
            for rgx in self.localhost_matchers:
                if re.match(rgx, element):
                    return True

        def first(self):
            return self and self[0] or None

    hosts = DistinctList().append(socket.getfqdn()).append(platform.node()).append(socket.gethostname())
    if not hosts:
        try:
            for a_nfo in socket.getaddrinfo(hosts.first() or 'localhost', None, socket.AF_INET,
                                            socket.SOCK_RAW, socket.IPPROTO_IP, socket.AI_CANONNAME):
                if len(a_nfo) > 3:
                    hosts.append(a_nfo[3])
        except socket.gaierror:
            log.warning('Cannot resolve address {addr} info via socket: {message}'.format(
                addr=hosts.first() or 'localhost (N/A)', message=socket.gaierror)
            )
    # Universal method for everywhere (Linux, Slowlaris, Windows etc)
    for f_name in ('/etc/hostname', '/etc/nodename', '/etc/hosts',
                   r'{win}\system32\drivers\etc\hosts'.format(win=os.getenv('WINDIR'))):
        try:
            with salt.utils.files.fopen(f_name) as f_hdl:
                for line in f_hdl:
                    line = salt.utils.stringutils.to_unicode(line)
                    hst = line.strip().split('#')[0].strip().split()
                    if hst:
                        if hst[0][:4] in ('127.', '::1') or len(hst) == 1:
                            hosts.extend(hst)
        except IOError:
            pass

    # include public and private ipaddresses
    return hosts.extend([addr for addr in ip_addrs()
                         if not ipaddress.ip_address(addr).is_loopback])