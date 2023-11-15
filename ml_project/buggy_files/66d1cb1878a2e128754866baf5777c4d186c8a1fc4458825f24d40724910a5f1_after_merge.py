def secret_edit(request, pk):

    secret = get_object_or_404(Secret, pk=pk)
    session_key = get_session_key(request)

    if request.method == 'POST':
        form = forms.SecretForm(request.POST, instance=secret)
        if form.is_valid():

            # Re-encrypt the Secret if a plaintext and session key have been provided.
            if form.cleaned_data['plaintext'] and session_key is not None:

                # Retrieve the master key using the provided session key
                master_key = None
                try:
                    sk = SessionKey.objects.get(userkey__user=request.user)
                    master_key = sk.get_master_key(session_key)
                except SessionKey.DoesNotExist:
                    form.add_error(None, "No session key found for this user.")

                # Create and encrypt the new Secret
                if master_key is not None:
                    secret = form.save(commit=False)
                    secret.plaintext = str(form.cleaned_data['plaintext'])
                    secret.encrypt(master_key)
                    secret.save()
                    messages.success(request, u"Modified secret {}.".format(secret))
                    return redirect('secrets:secret', pk=secret.pk)
                else:
                    form.add_error(None, "Invalid session key. Unable to encrypt secret data.")

            # We can't save the plaintext without a session key.
            elif form.cleaned_data['plaintext']:
                form.add_error(None, "No session key was provided with the request. Unable to encrypt secret data.")

            # If no new plaintext was specified, a session key is not needed.
            else:
                secret = form.save()
                messages.success(request, u"Modified secret {}.".format(secret))
                return redirect('secrets:secret', pk=secret.pk)

    else:
        form = forms.SecretForm(instance=secret)

    return render(request, 'secrets/secret_edit.html', {
        'secret': secret,
        'form': form,
        'return_url': reverse('secrets:secret', kwargs={'pk': secret.pk}),
    })