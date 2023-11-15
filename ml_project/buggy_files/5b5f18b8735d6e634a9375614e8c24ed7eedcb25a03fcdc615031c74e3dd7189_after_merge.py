def parse_date(date: Any) -> Optional[datetime]:
    """Parse unix timestamps, iso format, and human-readable strings"""
    
    if date is None:
        return None

    if isinstance(date, datetime):
        return date
    
    if isinstance(date, (float, int)):
        date = str(date)

    if isinstance(date, str):
        return dateparser(date)

    raise ValueError('Tried to parse invalid date! {}'.format(date))