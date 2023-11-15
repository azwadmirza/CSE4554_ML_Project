    def _send_raw_email(self):
        self.queue[self.current]['starttime'] = datetime.now()
        self.UIqueue[self.current]['formStarttime'] = self.queue[self.current]['starttime']
        # self.queue[self.current]['status'] = STAT_STARTED
        self.UIqueue[self.current]['stat'] = STAT_STARTED
        obj=self.queue[self.current]
        # create MIME message
        msg = MIMEMultipart()
        msg['Subject'] = self.queue[self.current]['subject']
        msg['Message-Id'] = make_msgid('calibre-web')
        msg['Date'] = formatdate(localtime=True)
        text = self.queue[self.current]['text']
        msg.attach(MIMEText(text.encode('UTF-8'), 'plain', 'UTF-8'))
        if obj['attachment']:
            result = get_attachment(obj['filepath'], obj['attachment'])
            if result:
                msg.attach(result)
            else:
                self._handleError(u"Attachment not found")
                return

        msg['From'] = obj['settings']["mail_from"]
        msg['To'] = obj['recipent']

        use_ssl = int(obj['settings'].get('mail_use_ssl', 0))
        try:
            # convert MIME message to string
            fp = StringIO()
            gen = Generator(fp, mangle_from_=False)
            gen.flatten(msg)
            msg = fp.getvalue()

            # send email
            timeout = 600  # set timeout to 5mins

            org_stderr = sys.stderr
            sys.stderr = StderrLogger()

            if use_ssl == 2:
                self.asyncSMTP = email_SSL(obj['settings']["mail_server"], obj['settings']["mail_port"], timeout)
            else:
                self.asyncSMTP = email(obj['settings']["mail_server"], obj['settings']["mail_port"], timeout)

            # link to logginglevel
            if web.ub.config.config_log_level != logging.DEBUG:
                self.asyncSMTP.set_debuglevel(0)
            else:
                self.asyncSMTP.set_debuglevel(1)
            if use_ssl == 1:
                self.asyncSMTP.starttls()
            if obj['settings']["mail_password"]:
                self.asyncSMTP.login(str(obj['settings']["mail_login"]), str(obj['settings']["mail_password"]))
            self.asyncSMTP.sendmail(obj['settings']["mail_from"], obj['recipent'], msg)
            self.asyncSMTP.quit()
            self._handleSuccess()
            sys.stderr = org_stderr

        except (MemoryError) as e:
            self._handleError(u'Error sending email: ' + e.message)
            return None
        except (smtplib.SMTPException) as e:
            if hasattr(e, "smtp_error"):
                text = e.smtp_error.replace("\n",'. ')
            else:
                text = ''
            self._handleError(u'Error sending email: ' + text)
            return None
        except (socket.error) as e:
            self._handleError(u'Error sending email: ' + e.strerror)
            return None