    def text(self, text):
        text = text.replace('<i>', codes['ITAL_START'])
        text = text.replace('</i>', codes['ITAL_END'])
        text = text.replace('<b>', codes['BOLD_START'])
        text = text.replace('</b>', codes['BOLD_END'])      
        visible_text = ''.join([c for c in text if c not in codes.values()])
        self._styles = [0,]*len(visible_text)
        self._text = visible_text
        
        current_style=0
        ci = 0
        for c in text:
            if c == codes['ITAL_START']:
                current_style += ITALIC
            elif c == codes['BOLD_START']:
                current_style += BOLD
            elif c == codes['BOLD_END']:
                current_style -= BOLD
            elif c == codes['ITAL_END']:
                current_style -= ITALIC
            else:
                self._styles[ci]=current_style
                ci+=1
                
        self._layout()