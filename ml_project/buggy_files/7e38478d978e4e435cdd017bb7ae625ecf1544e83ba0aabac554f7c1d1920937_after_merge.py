    def get_pre_post(self, client, node, replaceEnt):
        pre = ''
        if node['ids']:
            if node['ids'][0] not in client.targets:
                pre = u'<a name="%s"/>' % node['ids'][0]
                client.targets.append(node['ids'][0])
        else:
            name = node['names'][0]
            if name:
                pre = '<a name="%s"/>' % name
                client.targets.append(name)
        return pre, ''