        def replacement(m):
            language = m.group(1) or ''
            code = m.group(2)
            code = code.replace('&amp;', '&')
            code = code.replace('&gt;', '>')
            code = code.replace('&lt;', '<')
            code = code.replace('&quot;', '"')
            return '```{language}\n{code}\n```'.format(language=language, code=code)