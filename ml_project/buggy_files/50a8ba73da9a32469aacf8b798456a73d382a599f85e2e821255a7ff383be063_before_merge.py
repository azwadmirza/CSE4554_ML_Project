def domain(domain_name, max_users=-1, max_aliases=-1, max_quota_bytes=0):
    domain = models.Domain.query.get(domain_name)
    if not domain:
        domain = models.Domain(name=domain_name)
        db.session.add(domain)
        db.session.commit()