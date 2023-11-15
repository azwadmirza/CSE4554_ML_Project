    def discover(self):
        """Manual discovery."""
        # Accounts
        self.register(User, WeblateUserAdmin)
        self.register(Role, RoleAdmin)
        self.register(Group, WeblateGroupAdmin)
        self.register(AuditLog, AuditLogAdmin)
        self.register(AutoGroup, AutoGroupAdmin)
        self.register(Profile, ProfileAdmin)
        self.register(VerifiedEmail, VerifiedEmailAdmin)

        # Languages
        if settings.DEBUG:
            self.register(Language, LanguageAdmin)

        # Screenshots
        self.register(Screenshot, ScreenshotAdmin)

        # Fonts
        self.register(Font, FontAdmin)
        self.register(FontGroup, FontGroupAdmin)

        # Translations
        self.register(Project, ProjectAdmin)
        self.register(Component, ComponentAdmin)
        self.register(WhiteboardMessage, WhiteboardMessageAdmin)
        self.register(ComponentList, ComponentListAdmin)
        self.register(ContributorAgreement, ContributorAgreementAdmin)

        # Show some controls only in debug mode
        if settings.DEBUG:
            self.register(Translation, TranslationAdmin)
            self.register(Unit, UnitAdmin)
            self.register(Suggestion, SuggestionAdmin)
            self.register(Comment, CommentAdmin)
            self.register(Check, CheckAdmin)
            self.register(Dictionary, DictionaryAdmin)
            self.register(Change, ChangeAdmin)
            self.register(Source, SourceAdmin)

        if settings.BILLING_ADMIN:
            # Billing
            if 'weblate.billing' in settings.INSTALLED_APPS:
                # pylint: disable=wrong-import-position
                from weblate.billing.admin import (
                    PlanAdmin, BillingAdmin, InvoiceAdmin,
                )
                from weblate.billing.models import Plan, Billing, Invoice
                self.register(Plan, PlanAdmin)
                self.register(Billing, BillingAdmin)
                self.register(Invoice, InvoiceAdmin)

            # Hosted
            if 'wlhosted.integrations' in settings.INSTALLED_APPS:
                # pylint: disable=wrong-import-position
                from wlhosted.payments.admin import CustomerAdmin, PaymentAdmin
                from wlhosted.payments.models import Customer, Payment
                self.register(Customer, CustomerAdmin)
                self.register(Payment, PaymentAdmin)

        # Legal
        if 'weblate.legal' in settings.INSTALLED_APPS:
            # pylint: disable=wrong-import-position
            from weblate.legal.admin import AgreementAdmin
            from weblate.legal.models import Agreement
            self.register(Agreement, AgreementAdmin)

        # Python Social Auth
        self.register(UserSocialAuth, UserSocialAuthOption)
        self.register(Nonce, NonceOption)
        self.register(Association, AssociationOption)

        # Django REST Framework
        self.register(Token, TokenAdmin)

        # Django core
        self.register(Site, SiteAdmin)

        # Simple SSO
        if 'simple_sso.sso_server' in settings.INSTALLED_APPS:
            from simple_sso.sso_server.server import ConsumerAdmin
            from simple_sso.sso_server.models import Consumer
            self.register(Consumer, ConsumerAdmin)