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