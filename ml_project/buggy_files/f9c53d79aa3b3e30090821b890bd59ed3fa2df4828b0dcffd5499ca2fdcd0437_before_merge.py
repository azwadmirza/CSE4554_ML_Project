def os6_parse(lines, indent=None, comment_tokens=None):
    sublevel_cmds = [
        re.compile(r'^vlan.*$'),
        re.compile(r'^stack.*$'),
        re.compile(r'^interface.*$'),
        re.compile(r'datacenter-bridging.*$'),
        re.compile(r'line (console|telnet|ssh).*$'),
        re.compile(r'ip ssh !(server).*$'),
        re.compile(r'ip (dhcp|vrf).*$'),
        re.compile(r'(ip|mac|management|arp) access-list.*$'),
        re.compile(r'ipv6 (dhcp|router).*$'),
        re.compile(r'mail-server.*$'),
        re.compile(r'vpc domain.*$'),
        re.compile(r'router.*$'),
        re.compile(r'route-map.*$'),
        re.compile(r'policy-map.*$'),
        re.compile(r'class-map match-all.*$'),
        re.compile(r'captive-portal.*$'),
        re.compile(r'admin-profile.*$'),
        re.compile(r'link-dependency group.*$'),
        re.compile(r'banner motd.*$'),
        re.compile(r'openflow.*$'),
        re.compile(r'support-assist.*$'),
        re.compile(r'template.*$'),
        re.compile(r'address-family.*$'),
        re.compile(r'spanning-tree mst configuration.*$'),
        re.compile(r'logging.*$'),
        re.compile(r'(radius-server|tacacs-server) host.*$')]

    childline = re.compile(r'^exit$')
    config = list()
    parent = list()
    children = []
    parent_match = False
    for line in str(lines).split('\n'):
        text = str(re.sub(r'([{};])', '', line)).strip()
        cfg = ConfigLine(text)
        cfg.raw = line
        if not text or ignore_line(text, comment_tokens):
            parent = list()
            children = []
            continue

        else:
            parent_match = False
            # handle sublevel parent
            for pr in sublevel_cmds:
                if pr.match(line):
                    if len(parent) != 0:
                        cfg._parents.extend(parent)
                    parent.append(cfg)
                    config.append(cfg)
                    if children:
                        children.insert(len(parent) - 1, [])
                        children[len(parent) - 2].append(cfg)
                    parent_match = True
                    continue
            # handle exit
            if childline.match(line):
                if children:
                    parent[len(children) - 1]._children.extend(children[len(children) - 1])
                    if len(children) > 1:
                        parent[len(children) - 2]._children.extend(parent[len(children) - 1]._children)
                    cfg._parents.extend(parent)
                    children.pop()
                    parent.pop()
                if not children:
                    children = list()
                    if parent:
                        cfg._parents.extend(parent)
                    parent = list()
                config.append(cfg)
            # handle sublevel children
            elif parent_match is False and len(parent) > 0:
                if not children:
                    cfglist = [cfg]
                    children.append(cfglist)
                else:
                    children[len(parent) - 1].append(cfg)
                cfg._parents.extend(parent)
                config.append(cfg)
            # handle global commands
            elif not parent:
                config.append(cfg)
    return config