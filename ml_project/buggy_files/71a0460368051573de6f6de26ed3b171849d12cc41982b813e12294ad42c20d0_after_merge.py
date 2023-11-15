    def func(self):
        """
        Run the dynamic help entry creator.
        """
        query, cmdset = self.args, self.cmdset
        caller = self.caller

        suggestion_cutoff = self.suggestion_cutoff
        suggestion_maxnum = self.suggestion_maxnum

        if not query:
            query = "all"

        # removing doublets in cmdset, caused by cmdhandler
        # having to allow doublet commands to manage exits etc.
        cmdset.make_unique(caller)

        # retrieve all available commands and database topics
        all_cmds = [cmd for cmd in cmdset if self.check_show_help(cmd, caller)]
        all_topics = [topic for topic in HelpEntry.objects.all() if topic.access(caller, 'view', default=True)]
        all_categories = list(set([cmd.help_category.lower() for cmd in all_cmds] + [topic.help_category.lower()
                                                                                     for topic in all_topics]))

        if query in ("list", "all"):
            # we want to list all available help entries, grouped by category
            hdict_cmd = defaultdict(list)
            hdict_topic = defaultdict(list)
            # create the dictionaries {category:[topic, topic ...]} required by format_help_list
            # Filter commands that should be reached by the help
            # system, but not be displayed in the table.
            for cmd in all_cmds:
                if self.should_list_cmd(cmd, caller):
                    hdict_cmd[cmd.help_category].append(cmd.key)
            [hdict_topic[topic.help_category].append(topic.key) for topic in all_topics]
            # report back
            self.msg_help(self.format_help_list(hdict_cmd, hdict_topic))
            return

        # Try to access a particular command

        # build vocabulary of suggestions and rate them by string similarity.
        suggestions = None
        if suggestion_maxnum > 0:
            vocabulary = [cmd.key for cmd in all_cmds if cmd] + [topic.key for topic in all_topics] + all_categories
            [vocabulary.extend(cmd.aliases) for cmd in all_cmds]
            suggestions = [sugg for sugg in string_suggestions(query, set(vocabulary), cutoff=suggestion_cutoff,
                                                               maxnum=suggestion_maxnum)
                           if sugg != query]
            if not suggestions:
                suggestions = [sugg for sugg in vocabulary if sugg != query and sugg.startswith(query)]

        # try an exact command auto-help match
        match = [cmd for cmd in all_cmds if cmd == query]

        if not match:
            # try an inexact match with prefixes stripped from query and cmds
            _query = query[1:] if query[0] in CMD_IGNORE_PREFIXES else query

            match = [cmd for cmd in all_cmds
                    for m in cmd._matchset if m == _query or
                    m[0] in CMD_IGNORE_PREFIXES and m[1:] == _query]

        if len(match) == 1:
            formatted = self.format_help_entry(match[0].key,
                                               match[0].get_help(caller, cmdset),
                                               aliases=match[0].aliases,
                                               suggested=suggestions)
            self.msg_help(formatted)
            return

        # try an exact database help entry match
        match = list(HelpEntry.objects.find_topicmatch(query, exact=True))
        if len(match) == 1:
            formatted = self.format_help_entry(match[0].key,
                                               match[0].entrytext,
                                               aliases=match[0].aliases.all(),
                                               suggested=suggestions)
            self.msg_help(formatted)
            return

        # try to see if a category name was entered
        if query in all_categories:
            self.msg_help(self.format_help_list({query: [cmd.key for cmd in all_cmds if cmd.help_category == query]},
                                                {query: [topic.key for topic in all_topics
                                                         if topic.help_category == query]}))
            return

        # no exact matches found. Just give suggestions.
        self.msg((self.format_help_entry("", "No help entry found for '%s'" % query, None, suggested=suggestions), {"type": "help"}))