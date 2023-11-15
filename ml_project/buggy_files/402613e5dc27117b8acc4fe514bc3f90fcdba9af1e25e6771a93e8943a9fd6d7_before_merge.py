def store_user_details(sender, user, request, **kwargs):
    '''
    Stores user details on registration, here we rely on
    validation done by RegistrationForm.
    '''
    user.first_name = request.POST['first_name']
    user.last_name = request.POST['last_name']
    user.save()