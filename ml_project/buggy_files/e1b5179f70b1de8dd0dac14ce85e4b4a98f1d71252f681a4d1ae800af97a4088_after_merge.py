def get_billform_for(project, set_default=True, **kwargs):
    """Return an instance of BillForm configured for a particular project.

    :set_default: if set to True, on GET methods (usually when we want to
                  display the default form, it will call set_default on it.

    """
    form = BillForm(**kwargs)
    if form.original_currency.data == "None":
        form.original_currency.data = project.default_currency

    show_no_currency = form.original_currency.data == CurrencyConverter.no_currency

    form.original_currency.choices = [
        (currency_name, render_localized_currency(currency_name, detailed=False))
        for currency_name in form.currency_helper.get_currencies(
            with_no_currency=show_no_currency
        )
    ]

    active_members = [(m.id, m.name) for m in project.active_members]

    form.payed_for.choices = form.payer.choices = active_members
    form.payed_for.default = [m.id for m in project.active_members]

    if set_default and request.method == "GET":
        form.set_default()
    return form