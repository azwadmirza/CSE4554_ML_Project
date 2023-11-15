    def processcommand(cls, reader, command, replace=True, name=None):
        # Iterate through each word of the command substituting as
        # appropriate to construct the new command string. This
        # string is then broken up into exec argv components using
        # shlex.
        if replace:
            newcommand = ""
            for word in CommandParser(command).words():
                if word == "[]":
                    newcommand += reader.getposargs()
                    continue

                new_arg = ""
                new_word = reader._replace(word, name=name)
                new_word = reader._replace(new_word, name=name)
                new_word = Replacer._unescape(new_word)
                new_arg += new_word
                newcommand += new_arg
        else:
            newcommand = command

        # Construct shlex object that will not escape any values,
        # use all values as is in argv.
        shlexer = shlex.shlex(newcommand, posix=True)
        shlexer.whitespace_split = True
        shlexer.escape = ""
        return list(shlexer)