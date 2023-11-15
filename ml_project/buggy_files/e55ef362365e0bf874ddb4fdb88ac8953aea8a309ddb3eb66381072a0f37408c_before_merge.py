    def depart_title(self, node):
        close_tag = self.context[-1]
        if (self.permalink_text and self.builder.add_permalinks and
            node.parent.hasattr('ids') and node.parent['ids']):
            aname = node.parent['ids'][0]
            # add permalink anchor
            if close_tag.startswith('</h'):
                self.body.append(u'<a class="headerlink" href="#%s" ' % aname +
                                 u'title="%s">%s</a>' % (
                                 _('Permalink to this headline'),
                                 self.permalink_text))
            elif close_tag.startswith('</a></h'):
                self.body.append(u'</a><a class="headerlink" href="#%s" ' %
                                 aname +
                                 u'title="%s">%s' % (
                                 _('Permalink to this headline'),
                                 self.permalink_text))

        BaseTranslator.depart_title(self, node)