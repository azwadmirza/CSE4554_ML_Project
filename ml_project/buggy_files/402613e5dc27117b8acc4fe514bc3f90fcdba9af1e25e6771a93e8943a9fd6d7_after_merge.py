def store_user_details(sender, user, request, **kwargs):
    '''
    Stores user details on registration and creates user profile. We rely on
    validation done by RegistrationForm.
    '''
    user.first_name = request.POST['first_name']
    user.last_name = request.POST['last_name']
    user.save()
    profile, newprofile = Profile.objects.get_or_create(user = user)