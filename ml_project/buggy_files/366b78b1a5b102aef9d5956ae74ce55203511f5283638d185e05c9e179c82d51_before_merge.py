def on_mailbox_modified(mailbox):
    """Update amavis records if address has changed."""
    if parameters.get_admin("MANUAL_LEARNING") == "no" or \
       not hasattr(mailbox, "old_full_address") or \
       mailbox.full_address == mailbox.old_full_address:
        return
    user = Users.objects.select_related.get(email=mailbox.old_full_address)
    full_address = mailbox.full_address
    user.email = full_address
    user.policy.policy_name = full_address[:32]
    user.policy.sa_username = full_address
    user.policy.save()
    user.save()