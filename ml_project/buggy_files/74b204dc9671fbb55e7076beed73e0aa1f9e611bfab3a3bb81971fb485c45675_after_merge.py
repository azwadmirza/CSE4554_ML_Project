def edit_mailsettings():
    content = ub.session.query(ub.Settings).first()
    if request.method == "POST":
        to_save = request.form.to_dict()
        content.mail_server = to_save["mail_server"]
        content.mail_port = int(to_save["mail_port"])
        content.mail_login = to_save["mail_login"]
        content.mail_password = to_save["mail_password"]
        content.mail_from = to_save["mail_from"]
        content.mail_use_ssl = int(to_save["mail_use_ssl"])
        try:
            ub.session.commit()
        except Exception as e:
            flash(e, category="error")
        if "test" in to_save and to_save["test"]:
            if current_user.kindle_mail:
                result = helper.send_test_mail(current_user.kindle_mail, current_user.nickname)
                if result is None:
                    flash(_(u"Test e-mail successfully send to %(kindlemail)s", kindlemail=current_user.kindle_mail),
                          category="success")
                else:
                    flash(_(u"There was an error sending the Test e-mail: %(res)s", res=result), category="error")
            else:
                flash(_(u"Please configure your kindle e-mail address first..."), category="error")
        else:
            flash(_(u"E-mail server settings updated"), category="success")
    return render_title_template("email_edit.html", content=content, title=_(u"Edit e-mail server settings"),
                                 page="mailset")