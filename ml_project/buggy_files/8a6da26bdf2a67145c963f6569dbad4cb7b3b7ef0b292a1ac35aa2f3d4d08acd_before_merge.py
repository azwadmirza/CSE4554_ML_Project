    def notify(self, title, body, **kwargs):
        """
        Perform Email Notification
        """

        from_name = self.from_name
        if not from_name:
            from_name = self.app_desc

        self.logger.debug('Email From: %s <%s>' % (
            self.from_addr, from_name))
        self.logger.debug('Email To: %s' % (self.to_addr))
        self.logger.debug('Login ID: %s' % (self.user))
        self.logger.debug('Delivery: %s:%d' % (self.smtp_host, self.port))

        # Prepare Email Message
        if self.notify_format == NotifyFormat.HTML:
            email = MIMEText(body, 'html')
            email['Content-Type'] = 'text/html'

        else:
            email = MIMEText(body, 'text')
            email['Content-Type'] = 'text/plain'

        email['Subject'] = title
        email['From'] = '%s <%s>' % (from_name, self.from_addr)
        email['To'] = self.to_addr
        email['Date'] = datetime.utcnow()\
                                .strftime("%a, %d %b %Y %H:%M:%S +0000")
        email['X-Application'] = self.app_id

        try:
            self.logger.debug('Connecting to remote SMTP server...')
            socket = smtplib.SMTP(
                self.smtp_host,
                self.port,
                None,
                timeout=self.timeout,
            )

            if self.secure:
                # Handle Secure Connections
                self.logger.debug('Securing connection with TLS...')
                socket.starttls()

            if self.user and self.password:
                # Apply Login credetials
                self.logger.debug('Applying user credentials...')
                socket.login(self.user, self.password)

            # Send the email
            socket.sendmail(self.from_addr, self.to_addr, email.as_string())

            self.logger.info('Sent Email notification to "%s".' % (
                self.to_addr,
            ))

        except (SocketError, smtplib.SMTPException, RuntimeError) as e:
            self.logger.warning(
                'A Connection error occured sending Email '
                'notification to %s.' % self.smtp_host)
            self.logger.debug('Socket Exception: %s' % str(e))
            # Return; we're done
            return False

        finally:
            # Gracefully terminate the connection with the server
            socket.quit()

        return True