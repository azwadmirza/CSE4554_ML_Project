    def _format_string(self, string, rest, allow_recursion=True):
        values = []
        ret = Result()

        while True:
           # Look for the next replacement field, and get the
           # plain text before it.
           match = re.search(r'\{\{?|\}\}?', rest)
           if match:
              literal_chars = rest[: match.start()]
              if match.group() == '}':
                  raise self._syntax_error(string,
                      "f-string: single '}' is not allowed")
              if match.group() in ('{{', '}}'):
                  # Doubled braces just add a single brace to the text.
                  literal_chars += match.group()[0]
              rest = rest[match.end() :]
           else:
              literal_chars = rest
              rest = ""
           if literal_chars:
               values.append(asty.Str(string, s = literal_chars))
           if not rest:
               break
           if match.group() != '{':
               continue

           # Look for the end of the replacement field, allowing
           # one more level of matched braces, but no deeper, and only
           # if we can recurse.
           match = re.match(
               r'(?: \{ [^{}]* \} | [^{}]+ )* \}'
                   if allow_recursion
                   else r'[^{}]* \}',
               rest, re.VERBOSE)
           if not match:
              raise self._syntax_error(string, 'f-string: mismatched braces')
           item = rest[: match.end() - 1]
           rest = rest[match.end() :]

           # Parse the first form.
           try:
               model, item = parse_one_thing(item)
           except (ValueError, LexException) as e:
               raise self._syntax_error(string, "f-string: " + str(e))

           # Look for a conversion character.
           item = item.lstrip()
           conversion = None
           if item.startswith('!'):
               conversion = item[1]
               item = item[2:].lstrip()

           # Look for a format specifier.
           format_spec = asty.Str(string, s = "")
           if item.startswith(':'):
               if allow_recursion:
                   ret += self._format_string(string,
                       item[1:],
                       allow_recursion=False)
                   format_spec = ret.force_expr
               else:
                   format_spec = asty.Str(string, s=item[1:])
           elif item:
               raise self._syntax_error(string,
                   "f-string: trailing junk in field")

           # Now, having finished compiling any recursively included
           # forms, we can compile the first form that we parsed.
           ret += self.compile(model)

           if PY36:
               values.append(asty.FormattedValue(
                   string,
                   conversion = -1 if conversion is None else ord(conversion),
                   format_spec = format_spec,
                   value = ret.force_expr))
           else:
               # Make an expression like:
               #    "{!r:{}}".format(value, format_spec)
               values.append(asty.Call(string,
                   func = asty.Attribute(
                       string,
                       value = asty.Str(string, s =
                           '{' +
                           ('!' + conversion if conversion else '') +
                           ':{}}'),
                       attr = 'format', ctx = ast.Load()),
                   args = [ret.force_expr, format_spec],
                   keywords = [], starargs = None, kwargs = None))

        return ret + (
           asty.JoinedStr(string, values = values)
           if PY36
           else reduce(
              lambda x, y:
                  asty.BinOp(string, left = x, op = ast.Add(), right = y),
              values))