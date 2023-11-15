    def depart_desc_signature(self, node):
        if node['ids'] and self.permalink_text and self.builder.add_permalinks:
            self.body.append(u'<a class="headerlink" href="#%s" '
                             % node['ids'][0] +
                             u'title="%s">%s</a>' % (
                             _('Permalink to this definition'),
                             self.permalink_text))
        self.body.append('</dt>\n')