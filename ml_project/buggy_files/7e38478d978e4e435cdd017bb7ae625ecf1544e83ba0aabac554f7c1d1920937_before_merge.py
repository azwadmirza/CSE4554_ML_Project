    def get_pre_post(self, client, node, replaceEnt):
        pre = ''
        if node['ids']:
            if node['ids'][0] not in client.targets:
                pre = u'<a name="%s"/>' % node['ids'][0]
                client.targets.append(node['ids'][0])
        else:
            for attr in ['refid', 'refuri']:
                value = node.get(attr)
                if value:
                    pre = '<a name="%s"/>' % value
                    client.targets.append(value)
                    break
            else:
                raise ValueError(
                    "Target node '%s' doesn't have neither 'refid' or 'refuri'" % node
                )
        return pre, ''