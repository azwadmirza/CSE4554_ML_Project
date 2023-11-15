    def run(self, text):
        """ Iterate over html stash and restore html. """
        replacements = OrderedDict()
        for i in range(self.md.htmlStash.html_counter):
            html = self.md.htmlStash.rawHtmlBlocks[i]
            if self.isblocklevel(html):
                replacements["<p>%s</p>" %
                             (self.md.htmlStash.get_placeholder(i))] = \
                    html + "\n"
            replacements[self.md.htmlStash.get_placeholder(i)] = html

        if replacements:
            pattern = re.compile("|".join(re.escape(k) for k in replacements))
            processed_text = pattern.sub(lambda m: replacements[m.group(0)], text)
        else:
            return text

        if processed_text == text:
            return processed_text
        else:
            return self.run(processed_text)