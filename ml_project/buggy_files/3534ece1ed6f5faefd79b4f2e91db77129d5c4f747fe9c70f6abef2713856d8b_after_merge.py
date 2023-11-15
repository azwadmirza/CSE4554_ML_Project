def edit_project():
    edit_form = EditProjectForm()
    import_form = UploadForm()
    # Import form
    if import_form.validate_on_submit():
        try:
            import_project(import_form.file.data.stream, g.project)
            flash(_("Project successfully uploaded"))

            return redirect(url_for("main.list_bills"))
        except ValueError:
            flash(_("Invalid JSON"), category="danger")

    # Edit form
    if edit_form.validate_on_submit():
        project = edit_form.update(g.project)
        # Update converted currency
        if project.default_currency != CurrencyConverter.no_currency:
            for bill in project.get_bills():

                if bill.original_currency == CurrencyConverter.no_currency:
                    bill.original_currency = project.default_currency

                bill.converted_amount = CurrencyConverter().exchange_currency(
                    bill.amount, bill.original_currency, project.default_currency
                )
                db.session.add(bill)

        db.session.add(project)
        db.session.commit()

        return redirect(url_for("main.list_bills"))
    else:
        edit_form.name.data = g.project.name

        if g.project.logging_preference != LoggingMode.DISABLED:
            edit_form.project_history.data = True
            if g.project.logging_preference == LoggingMode.RECORD_IP:
                edit_form.ip_recording.data = True

        edit_form.contact_email.data = g.project.contact_email
        edit_form.default_currency.data = g.project.default_currency

    return render_template(
        "edit_project.html",
        edit_form=edit_form,
        import_form=import_form,
        current_view="edit_project",
    )