        def v_element_visitor(parent_e, parent_v):
            '''Visit the given element, creating or updating the parent vnode.'''
            for e in parent_e:
                assert e.tag in ('v','vh'), e.tag
                if e.tag == 'vh':
                    parent_v._headString = g.toUnicode(e.text or '')
                    continue
                gnx = e.attrib['t']
                v = gnx2vnode.get(gnx)
                if v:
                    # A clone
                    parent_v.children.append(v)
                    v.parents.append(parent_v)
                    # The body overrides any previous body text.
                    body = g.toUnicode(gnx2body.get(gnx) or '')
                    assert g.isUnicode(body), body.__class__.__name__
                    v._bodyString = body
                else:
                    #@+<< Make a new vnode, linked to the parent >>
                    #@+node:ekr.20180605075042.1: *7* << Make a new vnode, linked to the parent >>
                    v = leoNodes.VNode(context=c, gnx=gnx)
                    gnx2vnode [gnx] = v
                    parent_v.children.append(v)
                    v.parents.append(parent_v)
                    body = g.toUnicode(gnx2body.get(gnx) or '')
                    assert g.isUnicode(body), body.__class__.__name__
                    v._bodyString = body
                    v._headString = 'PLACE HOLDER'
                    #@-<< Make a new vnode, linked to the parent >>
                    #@+<< handle all other v attributes >>
                    #@+node:ekr.20180605075113.1: *7* << handle all other v attributes >>
                    # Like fc.handleVnodeSaxAttrutes.
                    #
                    # The native attributes of <v> elements are a, t, vtag, tnodeList,
                    # marks, expanded, and descendentTnode/VnodeUnknownAttributes.
                    d = e.attrib
                    s = d.get('tnodeList', '')
                    tnodeList = s and s.split(',')
                    if tnodeList:
                        # This tnodeList will be resolved later.
                        v.tempTnodeList = tnodeList
                    s = d.get('descendentTnodeUnknownAttributes')
                    if s:
                        aDict = fc.getDescendentUnknownAttributes(s, v=v)
                        if aDict:
                            fc.descendentTnodeUaDictList.append(aDict)
                    s = d.get('descendentVnodeUnknownAttributes')
                    if s:
                        aDict = fc.getDescendentUnknownAttributes(s, v=v)
                        if aDict:
                            fc.descendentVnodeUaDictList.append((v, aDict),)
                    #
                    # Handle vnode uA's
                    uaDict = gnx2ua.get(gnx)
                        # gnx2ua is a defaultdict(dict)
                        # It might already exists because of tnode uA's.
                    for key, val in d.items():
                        if key not in self.nativeVnodeAttributes:
                            uaDict[key] = self.resolveUa(key, val)
                    if uaDict:
                        v.unknownAttributes = uaDict
                    #@-<< handle all other v attributes >>
                    # Handle all inner elements.
                    v_element_visitor(e, v)