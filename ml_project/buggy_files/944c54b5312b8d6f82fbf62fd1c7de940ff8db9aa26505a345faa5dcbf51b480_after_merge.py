    def _check_signature_and_format(self, signature_or_text, parameter=None):
        """
        LSP hints might provide docstrings instead of signatures.

        This method will check for multiple signatures (dict, type etc...) and
        format the text accordingly.
        """
        open_func_char = ''
        has_signature = False
        has_multisignature = False
        language = getattr(self, 'language', '').lower()
        signature_or_text = signature_or_text.replace('\\*', '*')

        # Remove special symbols that could itefere with ''.format
        signature_or_text = signature_or_text.replace('{', '&#123;')
        signature_or_text = signature_or_text.replace('}', '&#125;')

        lines = signature_or_text.split('\n')
        inspect_word = None

        if language == 'python':
            open_func_char = '('
            idx = signature_or_text.find(open_func_char)
            inspect_word = signature_or_text[:idx]
            name_plus_char = inspect_word + open_func_char

            # Signature type
            count = signature_or_text.count(name_plus_char)
            has_signature = open_func_char in lines[0]
            if len(lines) > 1:
                has_multisignature = count > 1 and name_plus_char in lines[1]
            else:
                has_multisignature = False

        if has_signature and not has_multisignature:
            for i, line in enumerate(lines):
                if line.strip() == '':
                    break

            if i == 0:
                signature = lines[0]
                extra_text = None
            else:
                signature = '\n'.join(lines[:i])
                extra_text = '\n'.join(lines[i:])

            if signature:
                new_signature = self._format_signature(
                    signatures=signature,
                    parameter=parameter,
                )
        elif has_multisignature:
            signature = signature_or_text.replace(name_plus_char,
                                                  '<br>' + name_plus_char)
            signature = signature[4:]  # Remove the first line break
            signature = signature.replace('\n', ' ')
            signature = signature.replace(r'\\*', '*')
            signature = signature.replace(r'\*', '*')
            signature = signature.replace('<br>', '\n')
            signatures = signature.split('\n')
            signatures = [sig for sig in signatures if sig]  # Remove empty

            new_signature = self._format_signature(
                signatures=signatures,
                parameter=parameter,
            )
            extra_text = None
        else:
            new_signature = None
            extra_text = signature_or_text

        return new_signature, extra_text, inspect_word