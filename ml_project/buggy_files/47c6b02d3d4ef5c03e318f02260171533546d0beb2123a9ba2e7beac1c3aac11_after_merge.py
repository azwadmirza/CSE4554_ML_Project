    def transform_code(self, content):
        # http://en.support.wordpress.com/code/posting-source-code/. There are
        # a ton of things not supported here. We only do a basic [code
        # lang="x"] -> ```x translation, and remove quoted html entities (<,
        # >, &, and ").
        def replacement(m, c=content):
            if len(m.groups()) == 1:
                language = ''
                code = m.group(0)
            else:
                language = m.group(1) or ''
                code = m.group(2)
            code = code.replace('&amp;', '&')
            code = code.replace('&gt;', '>')
            code = code.replace('&lt;', '<')
            code = code.replace('&quot;', '"')
            return '```{language}\n{code}\n```'.format(language=language, code=code)

        content = self.code_re1.sub(replacement, content)
        content = self.code_re2.sub(replacement, content)
        content = self.code_re3.sub(replacement, content)
        content = self.code_re4.sub(replacement, content)
        return content