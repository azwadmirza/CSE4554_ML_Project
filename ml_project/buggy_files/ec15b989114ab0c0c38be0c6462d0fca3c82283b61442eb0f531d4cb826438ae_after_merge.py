def secret_add(request, pk):

    # Retrieve device
    device = get_object_or_404(Device, pk=pk)

    secret = Secret(device=device)
    session_key = get_session_key(request)

    if request.method == 'POST':
        form = forms.SecretForm(request.POST, instance=secret)
        if form.is_valid():

            # We need a valid session key in order to create a Secret
            if session_key is None:
                form.add_error(None, "No session key was provided with the request. Unable to encrypt secret data.")

            # Create and encrypt the new Secret
            else:
                master_key = None
                try:
                    sk = SessionKey.objects.get(userkey__user=request.user)
                    master_key = sk.get_master_key(session_key)
                except SessionKey.DoesNotExist:
                    form.add_error(None, "No session key found for this user.")

                if master_key is not None:
                    secret = form.save(commit=False)
                    secret.plaintext = str(form.cleaned_data['plaintext'])
                    secret.encrypt(master_key)
                    secret.save()
                    messages.success(request, u"Added new secret: {}.".format(secret))
                    if '_addanother' in request.POST:
                        return redirect('dcim:device_addsecret', pk=device.pk)
                    else:
                        return redirect('secrets:secret', pk=secret.pk)

    else:
        form = forms.SecretForm(instance=secret)

    return render(request, 'secrets/secret_edit.html', {
        'secret': secret,
        'form': form,
        'return_url': device.get_absolute_url(),
    })