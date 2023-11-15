def ticket_from_message(message, queue, logger):
    # 'message' must be an RFC822 formatted message.
    message = email.message_from_string(message) if six.PY3 else email.message_from_string(message.encode('utf-8'))
    subject = message.get('subject', _('Comment from e-mail'))
    subject = decode_mail_headers(decodeUnknown(message.get_charset(), subject))
    for affix in STRIPPED_SUBJECT_STRINGS:
        subject = subject.replace(affix, "")
    subject = subject.strip()

    sender = message.get('from', _('Unknown Sender'))
    sender = decode_mail_headers(decodeUnknown(message.get_charset(), sender))
    sender_email = email.utils.parseaddr(sender)[1]

    cc = message.get_all('cc', None)
    if cc:
        # first, fixup the encoding if necessary
        cc = [decode_mail_headers(decodeUnknown(message.get_charset(), x)) for x in cc]
        # get_all checks if multiple CC headers, but individual emails may be comma separated too
        tempcc = []
        for hdr in cc:
            tempcc.extend(hdr.split(','))
        # use a set to ensure no duplicates
        cc = set([x.strip() for x in tempcc])

    for ignore in IgnoreEmail.objects.filter(Q(queues=queue) | Q(queues__isnull=True)):
        if ignore.test(sender_email):
            if ignore.keep_in_mailbox:
                # By returning 'False' the message will be kept in the mailbox,
                # and the 'True' will cause the message to be deleted.
                return False
            return True

    matchobj = re.match(r".*\[" + queue.slug + "-(?P<id>\d+)\]", subject)
    if matchobj:
        # This is a reply or forward.
        ticket = matchobj.group('id')
        logger.info("Matched tracking ID %s-%s" % (queue.slug, ticket))
    else:
        logger.info("No tracking ID matched.")
        ticket = None

    body = None
    counter = 0
    files = []

    for part in message.walk():
        if part.get_content_maintype() == 'multipart':
            continue

        name = part.get_param("name")
        if name:
            name = email.utils.collapse_rfc2231_value(name)

        if part.get_content_maintype() == 'text' and name is None:
            if part.get_content_subtype() == 'plain':
                body = EmailReplyParser.parse_reply(
                    decodeUnknown(part.get_content_charset(), part.get_payload(decode=True))
                )
                # workaround to get unicode text out rather than escaped text
                try:
                    body = body.encode('ascii').decode('unicode_escape')
                except UnicodeEncodeError:
                    body.encode('utf-8')
                logger.debug("Discovered plain text MIME part")
            else:
                files.append(
                    SimpleUploadedFile(_("email_html_body.html"), encoding.smart_bytes(part.get_payload()), 'text/html')
                )
                logger.debug("Discovered HTML MIME part")
        else:
            if not name:
                ext = mimetypes.guess_extension(part.get_content_type())
                name = "part-%i%s" % (counter, ext)
            payload = part.get_payload()
            if isinstance(payload, list):
                payload = payload.pop().as_string()
            payloadToWrite = payload
            try:
                logger.debug("Try to base64 decode the attachment payload")
                payloadToWrite = base64.decodestring(payload)
            except (binascii.Error, TypeError):
                logger.debug("Payload was not base64 encoded, using raw bytes")
                payloadToWrite = payload
            files.append(SimpleUploadedFile(name, part.get_payload(decode=True), mimetypes.guess_type(name)[0]))
            logger.debug("Found MIME attachment %s" % name)

        counter += 1

    if not body:
        mail = BeautifulSoup(part.get_payload(), "lxml")
        if ">" in mail.text:
            message_body = mail.text.split(">")[1]
            body = message_body.encode('ascii', errors='ignore')
        else:
            body = mail.text

    if ticket:
        try:
            t = Ticket.objects.get(id=ticket)
        except Ticket.DoesNotExist:
            logger.info("Tracking ID %s-%s not associated with existing ticket. Creating new ticket." % (queue.slug, ticket))
            ticket = None
        else:
            logger.info("Found existing ticket with Tracking ID %s-%s" % (t.queue.slug, t.id))
            if t.status == Ticket.CLOSED_STATUS:
                t.status = Ticket.REOPENED_STATUS
                t.save()
            new = False

    smtp_priority = message.get('priority', '')
    smtp_importance = message.get('importance', '')
    high_priority_types = {'high', 'important', '1', 'urgent'}
    priority = 2 if high_priority_types & {smtp_priority, smtp_importance} else 3

    if ticket is None:
        if settings.QUEUE_EMAIL_BOX_UPDATE_ONLY:
            return None
        new = True
        t = Ticket.objects.create(
            title=subject,
            queue=queue,
            submitter_email=sender_email,
            created=timezone.now(),
            description=body,
            priority=priority,
        )
        logger.debug("Created new ticket %s-%s" % (t.queue.slug, t.id))

    if cc:
        # get list of currently CC'd emails
        current_cc = TicketCC.objects.filter(ticket=ticket)
        current_cc_emails = [x.email for x in current_cc if x.email]
        # get emails of any Users CC'd to email, if defined
        # (some Users may not have an associated email, e.g, when using LDAP)
        current_cc_users = [x.user.email for x in current_cc if x.user and x.user.email]
        # ensure submitter, assigned user, queue email not added
        other_emails = [queue.email_address]
        if t.submitter_email:
            other_emails.append(t.submitter_email)
        if t.assigned_to:
            other_emails.append(t.assigned_to.email)
        current_cc = set(current_cc_emails + current_cc_users + other_emails)
        # first, add any User not previously CC'd (as identified by User's email)
        all_users = User.objects.all()
        all_user_emails = set([x.email for x in all_users])
        users_not_currently_ccd = all_user_emails.difference(set(current_cc))
        users_to_cc = cc.intersection(users_not_currently_ccd)
        for user in users_to_cc:
            tcc = TicketCC.objects.create(
                ticket=t,
                user=User.objects.get(email=user),
                can_view=True,
                can_update=False
            )
            tcc.save()
        # then add remaining emails alphabetically, makes testing easy
        new_cc = cc.difference(current_cc).difference(all_user_emails)
        new_cc = sorted(list(new_cc))
        for ccemail in new_cc:
            tcc = TicketCC.objects.create(
                ticket=t,
                email=ccemail,
                can_view=True,
                can_update=False
            )
            tcc.save()

    f = FollowUp(
        ticket=t,
        title=_('E-Mail Received from %(sender_email)s' % {'sender_email': sender_email}),
        date=timezone.now(),
        public=True,
        comment=body,
    )

    if t.status == Ticket.REOPENED_STATUS:
        f.new_status = Ticket.REOPENED_STATUS
        f.title = _('Ticket Re-Opened by E-Mail Received from %(sender_email)s' % {'sender_email': sender_email})

    f.save()
    logger.debug("Created new FollowUp for Ticket")

    if six.PY2:
        logger.info(("[%s-%s] %s" % (t.queue.slug, t.id, t.title,)).encode('ascii', 'replace'))
    elif six.PY3:
        logger.info("[%s-%s] %s" % (t.queue.slug, t.id, t.title,))

    attached = process_attachments(f, files)
    for att_file in attached:
        logger.info("Attachment '%s' (with size %s) successfully added to ticket from email." % (att_file[0], att_file[1].size))

    context = safe_template_context(t)

    if new:
        if sender_email:
            send_templated_mail(
                'newticket_submitter',
                context,
                recipients=sender_email,
                sender=queue.from_address,
                fail_silently=True,
            )
        if queue.new_ticket_cc:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=queue.new_ticket_cc,
                sender=queue.from_address,
                fail_silently=True,
            )
        if queue.updated_ticket_cc and queue.updated_ticket_cc != queue.new_ticket_cc:
            send_templated_mail(
                'newticket_cc',
                context,
                recipients=queue.updated_ticket_cc,
                sender=queue.from_address,
                fail_silently=True,
            )
    else:
        context.update(comment=f.comment)
        if t.assigned_to:
            send_templated_mail(
                'updated_owner',
                context,
                recipients=t.assigned_to.email,
                sender=queue.from_address,
                fail_silently=True,
            )
        if queue.updated_ticket_cc:
            send_templated_mail(
                'updated_cc',
                context,
                recipients=queue.updated_ticket_cc,
                sender=queue.from_address,
                fail_silently=True,
            )

    return t