    def import_task_choice_event(self, session, task):
        skip_queries = self.config['skip'].as_str_seq()
        warn_queries = self.config['warn'].as_str_seq()

        if task.choice_flag == action.APPLY:
            if skip_queries or warn_queries:
                self._log.debug('[ihate] processing your hate')
                if self.do_i_hate_this(task, skip_queries):
                    task.choice_flag = action.SKIP
                    self._log.info(u'[ihate] skipped: {0}'
                                   .format(summary(task)))
                    return
                if self.do_i_hate_this(task, warn_queries):
                    self._log.info(u'[ihate] you maybe hate this: {0}'
                                   .format(summary(task)))
            else:
                self._log.debug('[ihate] nothing to do')
        else:
            self._log.debug('[ihate] user made a decision, nothing to do')