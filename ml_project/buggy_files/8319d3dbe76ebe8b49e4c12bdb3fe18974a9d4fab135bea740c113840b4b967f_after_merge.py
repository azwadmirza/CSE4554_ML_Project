    def convert_calibre(self):
        error_message = None
        file_path = self.queue[self.current]['file_path']
        bookid = self.queue[self.current]['bookid']
        if not os.path.exists(web.ub.config.config_converterpath):
            error_message = _(u"Ebook-convert binary %(converterpath)s not found",
                              converterpath=web.ub.config.config_converterpath)
            web.app.logger.error("convert_calibre: " + error_message)
            self.queue[self.current]['status'] = STAT_FAIL
            self.UIqueue[self.current]['status'] = _('Failed')
            self.UIqueue[self.current]['progress'] = "100 %"
            self.UIqueue[self.current]['runtime'] = self._formatRuntime(
                                                    datetime.now() - self.queue[self.current]['starttime'])
            self.UIqueue[self.current]['message'] = error_message
            return
        try:
            command = (u"\"" + web.ub.config.config_converterpath + u"\" \"" + file_path + u".epub\" \""
                       + file_path + u".mobi\" " + web.ub.config.config_calibre).encode(sys.getfilesystemencoding())
            if sys.version_info > (3, 0):
                p = subprocess.Popen(command.decode('Utf-8'), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            else:
                p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        except Exception as e:
            error_message = _(u"Ebook-convert failed, no execution permissions")
            web.app.logger.error("convert_calibre: " + error_message)
            self.queue[self.current]['status'] = STAT_FAIL
            self.UIqueue[self.current]['status'] = _('Failed')
            self.UIqueue[self.current]['progress'] = "100 %"
            self.UIqueue[self.current]['runtime'] = self._formatRuntime(
                                                    datetime.now() - self.queue[self.current]['starttime'])
            self.UIqueue[self.current]['message'] = error_message
            return # error_message, RET_FAIL
        # Poll process for new output until finished
        while True:
            nextline = p.stdout.readline()
            if sys.version_info > (3, 0):
                nextline = nextline.decode('Utf-8','backslashreplace')
            if nextline == '' and p.poll() is not None:
                break
            progress = re.search("(\d+)%\s.*", nextline)
            if progress:
                self.UIqueue[self.current]['progress'] = progress.group(1) + '%'
            if sys.version_info > (3, 0):
                web.app.logger.debug(nextline.strip('\r\n'))
            else:
                web.app.logger.debug(nextline.strip('\r\n').decode(sys.getfilesystemencoding()))


        check = p.returncode
        if check == 0:
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
            return file_path + ".mobi" # , RET_SUCCESS
        else:
            web.app.logger.info("convert_calibre: Ebook-convert failed with error while converting book")
            if not error_message:
                error_message = 'Ebook-convert failed, no excecution permissions'
            self.queue[self.current]['status'] = STAT_FAIL
            self.UIqueue[self.current]['status'] = _('Failed')
            self.UIqueue[self.current]['progress'] = "100 %"
            self.UIqueue[self.current]['runtime'] = self._formatRuntime(
                                                    datetime.now() - self.queue[self.current]['starttime'])
            self.UIqueue[self.current]['message'] = error_message
            return # error_message, RET_FAIL