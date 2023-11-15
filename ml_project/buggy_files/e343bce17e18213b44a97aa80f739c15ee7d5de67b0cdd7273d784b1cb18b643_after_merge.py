    def _convert_ebook_format(self):
        error_message = None
        file_path = self.queue[self.current]['file_path']
        bookid = self.queue[self.current]['bookid']
        format_old_ext = u'.' + self.queue[self.current]['settings']['old_book_format'].lower()
        format_new_ext = u'.' + self.queue[self.current]['settings']['new_book_format'].lower()

        # check to see if destination format already exists -
        # if it does - mark the conversion task as complete and return a success
        # this will allow send to kindle workflow to continue to work
        if os.path.isfile(file_path + format_new_ext):
            web.app.logger.info("Book id %d already converted to %s", bookid, format_new_ext)
            cur_book = web.db.session.query(web.db.Books).filter(web.db.Books.id == bookid).first()
            self.queue[self.current]['path'] = file_path
            self.queue[self.current]['title'] = cur_book.title
            self._handleSuccess()
            return file_path + format_new_ext
        else:
            web.app.logger.info("Book id %d - target format of %s does not exist. Moving forward with convert.",
                                bookid, format_new_ext)

        # check if converter-executable is existing
        if not os.path.exists(web.ub.config.config_converterpath):
            # ToDo Text is not translated
            self._handleError(u"Convertertool %s not found" % web.ub.config.config_converterpath)
            return

        try:
            # check which converter to use kindlegen is "1"
            if format_old_ext == '.epub' and format_new_ext == '.mobi':
                if web.ub.config.config_ebookconverter == 1:
                    if os.name == 'nt':
                        command = web.ub.config.config_converterpath + u' "' + file_path + u'.epub"'
                        if sys.version_info < (3, 0):
                            command = command.encode(sys.getfilesystemencoding())
                    else:
                        command = [web.ub.config.config_converterpath, file_path + u'.epub']
                        if sys.version_info < (3, 0):
                            command = [x.encode(sys.getfilesystemencoding()) for x in command]
            if web.ub.config.config_ebookconverter == 2:
                # Linux py2.7 encode as list without quotes no empty element for parameters
                # linux py3.x no encode and as list without quotes no empty element for parameters
                # windows py2.7 encode as string with quotes empty element for parameters is okay
                # windows py 3.x no encode and as string with quotes empty element for parameters is okay
                # separate handling for windows and linux
                if os.name == 'nt':
                    command = web.ub.config.config_converterpath + u' "' + file_path + format_old_ext + u'" "' + \
                              file_path + format_new_ext + u'" ' + web.ub.config.config_calibre
                    if sys.version_info < (3, 0):
                        command = command.encode(sys.getfilesystemencoding())
                else:
                    command = [web.ub.config.config_converterpath, (file_path + format_old_ext),
                               (file_path + format_new_ext)]
                    if web.ub.config.config_calibre:
                        parameters = web.ub.config.config_calibre.split(" ")
                        for param in parameters:
                            command.append(param)
                    if sys.version_info < (3, 0):
                        command = [x.encode(sys.getfilesystemencoding()) for x in command]

            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        except OSError as e:
            self._handleError(_(u"Ebook-converter failed: %(error)s", error=e))
            return

        if web.ub.config.config_ebookconverter == 1:
            nextline = p.communicate()[0]
            # Format of error message (kindlegen translates its output texts):
            # Error(prcgen):E23006: Language not recognized in metadata.The dc:Language field is mandatory.Aborting.
            conv_error = re.search(".*\(.*\):(E\d+):\s(.*)", nextline, re.MULTILINE)
            # If error occoures, store error message for logfile
            if conv_error:
                error_message = _(u"Kindlegen failed with Error %(error)s. Message: %(message)s",
                                  error=conv_error.group(1), message=conv_error.group(2).strip())
            web.app.logger.debug("convert_kindlegen: " + nextline)
        else:
            while p.poll() is None:
                nextline = p.stdout.readline()
                if os.name == 'nt' and sys.version_info < (3, 0):
                    nextline = nextline.decode('windows-1252')
                web.app.logger.debug(nextline.strip('\r\n'))
                # parse progress string from calibre-converter
                progress = re.search("(\d+)%\s.*", nextline)
                if progress:
                    self.UIqueue[self.current]['progress'] = progress.group(1) + ' %'

        # process returncode
        check = p.returncode
        calibre_traceback = p.stderr.readlines()
        for ele in calibre_traceback:
            web.app.logger.debug(ele.strip('\n'))
            if not ele.startswith('Traceback') and not ele.startswith('  File'):
                error_message = "Calibre failed with error: %s" % ele.strip('\n')

        # kindlegen returncodes
        # 0 = Info(prcgen):I1036: Mobi file built successfully
        # 1 = Info(prcgen):I1037: Mobi file built with WARNINGS!
        # 2 = Info(prcgen):I1038: MOBI file could not be generated because of errors!
        if (check < 2 and web.ub.config.config_ebookconverter == 1) or \
            (check == 0 and web.ub.config.config_ebookconverter == 2):
            cur_book = web.db.session.query(web.db.Books).filter(web.db.Books.id == bookid).first()
            if os.path.isfile(file_path + format_new_ext):
                new_format = web.db.Data(name=cur_book.data[0].name,
                                         book_format=self.queue[self.current]['settings']['new_book_format'].upper(),
                                         book=bookid, uncompressed_size=os.path.getsize(file_path + format_new_ext))
                cur_book.data.append(new_format)
                web.db.session.commit()
                self.queue[self.current]['path'] = cur_book.path
                self.queue[self.current]['title'] = cur_book.title
                if web.ub.config.config_use_google_drive:
                    os.remove(file_path + format_old_ext)
                self._handleSuccess()
                return file_path + format_new_ext
            else:
                error_message = format_new_ext.upper() + ' format not found on disk'
        web.app.logger.info("ebook converter failed with error while converting book")
        if not error_message:
            error_message = 'Ebook converter failed with unknown error'
        self._handleError(error_message)
        return