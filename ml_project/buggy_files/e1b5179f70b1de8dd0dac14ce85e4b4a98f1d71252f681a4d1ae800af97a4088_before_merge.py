def get_billform_for(project, set_default=True, **kwargs):
    """Return an instance of BillForm configured for a particular project.

    :set_default: if set to True, on GET methods (usually when we want to
                  display the default form, it will call set_default on it.

    """
    form = BillForm(**kwargs)
    if form.original_currency.data == "None":
        form.original_currency.data = project.default_currency

    if form.original_currency.data != CurrencyConverter.default:
        choices = copy.copy(form.original_currency.choices)
        choices.remove((CurrencyConverter.default, CurrencyConverter.default))
        choices.sort(
            key=lambda rates: "" if rates[0] == project.default_currency else rates[0]
        )
        form.original_currency.choices = choices
    else:
        form.original_currency.render_kw = {"default": True}
        form.original_currency.data = CurrencyConverter.default

    form.original_currency.label = Label(
        "original_currency", "Currency (Default: %s)" % (project.default_currency)
    )
    active_members = [(m.id, m.name) for m in project.active_members]

    form.payed_for.choices = form.payer.choices = active_members
    form.payed_for.default = [m.id for m in project.active_members]

    if set_default and request.method == "GET":
        form.set_default()
    return form