    def continuation_tokens(self, width, line_number, is_soft_wrap=False):
        """Displays dots in multiline prompt"""
        if is_soft_wrap:
            return ""
        width = width - 1
        dots = builtins.__xonsh__.env.get("MULTILINE_PROMPT")
        dots = dots() if callable(dots) else dots
        if not dots:
            return ""
        basetoks = self.format_color(dots)
        baselen = sum(len(t[1]) for t in basetoks)
        if baselen == 0:
            return [(Token, " " * (width + 1))]
        toks = basetoks * (width // baselen)
        n = width % baselen
        count = 0
        for tok in basetoks:
            slen = len(tok[1])
            newcount = slen + count
            if slen == 0:
                continue
            elif newcount <= n:
                toks.append(tok)
            else:
                toks.append((tok[0], tok[1][: n - count]))
            count = newcount
            if n <= count:
                break
        toks.append((Token, " "))  # final space
        return PygmentsTokens(toks)