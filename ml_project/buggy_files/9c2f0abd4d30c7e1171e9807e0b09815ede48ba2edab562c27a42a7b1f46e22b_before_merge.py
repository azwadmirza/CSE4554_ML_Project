    def convert_kindlegen(self):
        error_message = None
        file_path = self.queue[self.current]['file_path']
        bookid = self.queue[self.current]['bookid']
        if not os.path.exists(web.ub.config.config_converterpath):
            error_message = _(u"kindlegen binary %(kindlepath)s not found", kindlepath=web.ub.config.config_converterpath)
            web.app.logger.error("convert_kindlegen: " + error_message)
            self.queue[self.current]['status'] = STAT_FAIL
            self.UIqueue[self.current]['status'] = _('Failed')
            self.UIqueue[self.current]['progress'] = "100 %"
            self.UIqueue[self.current]['runtime'] = self._formatRuntime(
                                                    datetime.now() - self.queue[self.current]['starttime'])
            self.UIqueue[self.current]['message'] = error_message
            return
        try:
            p = subprocess.Popen(
                (web.ub.config.config_converterpath + " \"" + file_path + u".epub\"").encode(sys.getfilesystemencoding()),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        except Exception:
            error_message = _(u"kindlegen failed, no execution permissions")
            web.app.logger.error("convert_kindlegen: " + error_message)
            self.queue[self.current]['status'] = STAT_FAIL
            self.UIqueue[self.current]['status'] = _('Failed')
            self.UIqueue[self.current]['progress'] = "100 %"
            self.UIqueue[self.current]['runtime'] = self._formatRuntime(
                                                    datetime.now() - self.queue[self.current]['starttime'])
            self.UIqueue[self.current]['message'] = error_message
            return
        # Poll process for new output until finished
        while True:
            nextline = p.stdout.readline()
            if nextline == '' and p.poll() is not None:
                break
            if nextline != "\r\n":
                # Format of error message (kindlegen translates its output texts):
                # Error(prcgen):E23006: Language not recognized in metadata.The dc:Language field is mandatory.Aborting.
                conv_error = re.search(".*\(.*\):(E\d+):\s(.*)", nextline)
                # If error occoures, log in every case
                if conv_error:
                    error_message = _(u"Kindlegen failed with Error %(error)s. Message: %(message)s",
                                      error=conv_error.group(1), message=conv_error.group(2).decode('utf-8'))
                    web.app.logger.info("convert_kindlegen: " + error_message)
                    web.app.logger.info(nextline.strip('\r\n'))
                else:
                    web.app.logger.debug(nextline.strip('\r\n'))

        check = p.returncode
        if not check or check < 2:
            cur_book = web.db.session.query(web.db.Books).filter(web.db.Books.id == bookid).first()
            new_format = web.db.Data(name=cur_book.data[0].name,book_format="MOBI",
                                     book=bookid,uncompressed_size=os.path.getsize(file_path + ".mobi"))
            cur_book.data.append(new_format)
            web.db.session.commit()
            self.queue[self.current]['path'] = cur_book.path
            self.queue[self.current]['title'] = cur_book.title
            if web.ub.config.config_use_google_drive:
                os.remove(file_path + u".epub")
            self.queue[self.current]['status'] = STAT_FINISH_SUCCESS
            self.UIqueue[self.current]['status'] = _('Finished')
            self.UIqueue[self.current]['progress'] = "100 %"
            self.UIqueue[self.current]['runtime'] = self._formatRuntime(
                                                    datetime.now() - self.queue[self.current]['starttime'])
            return file_path + ".mobi" #, RET_SUCCESS
        else:
            web.app.logger.info("convert_kindlegen: kindlegen failed with error while converting book")
            if not error_message:
                error_message = 'kindlegen failed, no excecution permissions'
            self.queue[self.current]['status'] = STAT_FAIL
            self.UIqueue[self.current]['status'] = _('Failed')
            self.UIqueue[self.current]['progress'] = "100 %"
            self.UIqueue[self.current]['runtime'] = self._formatRuntime(
                                                    datetime.now() - self.queue[self.current]['starttime'])
            self.UIqueue[self.current]['message'] = error_message
            return # error_message, RET_FAIL