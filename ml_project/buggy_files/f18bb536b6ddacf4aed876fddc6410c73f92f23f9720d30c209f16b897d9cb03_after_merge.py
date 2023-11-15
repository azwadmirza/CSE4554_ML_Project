def edit_domain():
    ''' POST /post
        name:  'username',  //name of field (column in db)
        pk:    1            //primary key (record id)
        value: 'superuser!' //new value'''
    vals = request.form.to_dict()
    answer = ub.session.query(ub.Registration).filter(ub.Registration.id == vals['pk']).first()
    # domain_name = request.args.get('domain')
    answer.domain = vals['value'].replace('*','%').replace('?','_').lower()
    ub.session.commit()
    return ""