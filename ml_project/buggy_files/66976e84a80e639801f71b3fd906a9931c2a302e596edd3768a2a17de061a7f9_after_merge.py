def import_targets(request):
    context = {}
    context['import_target_li'] = 'active'
    context['target_data_active'] = 'true'
    if request.method == 'POST':
        if 'txtFile' in request.FILES:
            txt_file = request.FILES['txtFile']
            if txt_file.content_type == 'text/plain':
                target_count = 0
                txt_content = txt_file.read().decode('UTF-8')
                io_string = io.StringIO(txt_content)
                for target in io_string:
                    if validators.domain(target):
                        Domain.objects.create(
                            domain_name=target.rstrip("\n"), insert_date=timezone.now())
                        target_count += 1
                if target_count:
                    messages.add_message(request, messages.SUCCESS, str(
                        target_count) + ' targets added successfully!')
                    return http.HttpResponseRedirect(reverse('list_target'))
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        'Oops! File format was invalid, could not import any targets.')
            else:
                messages.add_message(
                    request, messages.ERROR, 'Invalid File type!')
        elif 'csvFile' in request.FILES:
            csv_file = request.FILES['csvFile']
            if csv_file.content_type == 'text/csv':
                target_count = 0
                csv_content = csv_file.read().decode('UTF-8')
                io_string = io.StringIO(csv_content)
                for column in csv.reader(io_string, delimiter=','):
                    if validators.domain(column[0]):
                        Domain.objects.create(
                            domain_name=column[0],
                            domain_description=column[1],
                            insert_date=timezone.now())
                        target_count += 1
                if target_count:
                    messages.add_message(request, messages.SUCCESS, str(
                        target_count) + ' targets added successfully!')
                    return http.HttpResponseRedirect(reverse('list_target'))
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        'Oops! File format was invalid, could not import any targets.')
            else:
                messages.add_message(
                    request, messages.ERROR, 'Invalid File type!')
    return render(request, 'target/import.html', context)