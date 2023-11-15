    def store_dnsbl_result(self, domain, provider, results, **options):
        """Store DNSBL provider results for domain."""
        alerts = {}
        to_create = []
        for mx in results.keys():
            result = "" if not results[mx] else results[mx]
            dnsbl_result = models.DNSBLResult.objects.filter(
                domain=domain, provider=provider, mx=mx).first()
            trigger = False
            if dnsbl_result is None:
                to_create.append(
                    models.DNSBLResult(
                        domain=domain, provider=provider, mx=mx,
                        status=result)
                )
                if result:
                    trigger = True
            else:
                dnsbl_result.status = result
                dnsbl_result.save()
                if not dnsbl_result.status and result:
                    trigger = True
            if trigger:
                if domain not in alerts:
                    alerts[domain] = []
                alerts[domain].append((provider, mx))
        models.DNSBLResult.objects.bulk_create(to_create)
        if not alerts:
            return
        emails = list(options["email"])
        if not options["skip_admin_emails"]:
            emails.extend(
                domain.admins.exclude(mailbox__isnull=True)
                .values_list("email", flat=True)
            )
        if not len(emails):
            return
        with mail.get_connection() as connection:
            for domain, providers in list(alerts.items()):
                content = render_to_string(
                    "admin/notifications/domain_in_dnsbl.html", {
                        "domain": domain, "alerts": providers
                    })
                subject = _("[modoboa] DNSBL issue(s) for domain {}").format(
                    domain.name)
                msg = EmailMessage(
                    subject, content.strip(), self.sender, emails,
                    connection=connection
                )
                msg.send()