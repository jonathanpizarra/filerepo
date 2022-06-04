from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Log
from accounts.models import User
from file_manager.models import FileUpload
import json
from django.core import serializers
# Create your views here.
# log template
# Log(log_code='', log_message=f'{}').save()

PATH = 'files/'

def reports(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    user = get_object_or_404(User, pk=id)
    context = {
        'user' : user
    }

    return render(request, 'reports/index.html', context)

def get_users(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    
    users = User.objects.filter(is_admin=False, is_archived=False)
    data = []
    id_len = len('User ID')
    uname_len = len('Username')
    fname_len = len('Firstname')
    lname_len = len('Lastname')
    

    get_all = POST.get('get_all', '')

    if get_all == 'no':
        uname_filter = POST.get('username_filter', '')
        uname_input = POST.get('username_input', '').strip()
        
        fname_filter = POST.get('firstname_filter', '')
        fname_input = POST.get('firstname_input', '').strip()

        lname_filter = POST.get('lastname_filter', '')
        lname_input = POST.get('lastname_input', '').strip()

        cdate_filter = POST.get('creation_date_filter', '')
        
        if uname_filter != 'none' and uname_input != '':
            if uname_filter == 'starts_with':
                users = users.filter(username__istartswith=uname_input)
            elif uname_filter == 'ends_with':
                users = users.filter(username__iendswith=uname_input)
            elif uname_filter == 'contains':
                users = users.filter(username__icontains=uname_input)

        if fname_filter != 'none' and fname_input != '':
            if fname_filter == 'starts_with':
                users = users.filter(first_name__istartswith=fname_input)
            elif fname_filter == 'ends_with':
                users = users.filter(first_name__iendswith=fname_input)
            elif fname_filter == 'contains':
                users = users.filter(first_name__icontains=fname_input)

        if lname_filter != 'none' and fname_input != '':
            if lname_filter == 'starts_with':
                users = users.filter(last_name__istartswith=lname_input)
            elif lname_filter == 'ends_with':
                users = users.filter(last_name__iendswith=lname_input)
            elif lname_filter == 'contains':
                users = users.filter(last_name__icontains=lname_input)

        if cdate_filter != '':
            users = users.filter(creation_date__startswith=cdate_filter)
    
    if users.count() == 0:
        return JsonResponse({
            'result' : 'none',
            'message' : 'No users match the filters',
        })

    l = len(str(users.count()))

    for u in users:
        if len(str(u.id)) > id_len: id_len = len(str(u.id))
        if len(u.username) > uname_len: uname_len = len(u.username)
        if len(u.first_name) > fname_len: fname_len = len(u.first_name)
        if len(u.last_name) > lname_len: lname_len = len(u.last_name)
        data.append({
            'uid' : u.id,
            'uname': u.username,
            'fname' : u.first_name,
            'lname' : u.last_name,
            'is_archived' : u.is_archived,
            'cdate' : u.creation_date
        })
    pre = ''
    with open(f'media/reports/user_list_{id}.txt', 'w') as f:
        f.write('List of users\n\n')
        pre += 'List of users\n\n'
        f.write(f"{add_spaces('    ', l)}   {add_spaces('User ID', id_len)}   {add_spaces('Username', uname_len)}   {add_spaces('Firstname', fname_len)}   {add_spaces('Lastname', lname_len)}   Creation Date\n\n")
        pre += f"{add_spaces('    ', l)}   {add_spaces('User ID', id_len)}   {add_spaces('Username', uname_len)}   {add_spaces('Firstname', fname_len)}   {add_spaces('Lastname', lname_len)}   Creation Date\n\n"
        count = 1
        for d in data:
            f.write(f"{add_spaces(str(count) + '.  ', l)}   {add_spaces(str(d['uid']), id_len)}   {add_spaces(d['uname'], uname_len)}   {add_spaces(d['fname'], fname_len)}   {add_spaces(d['lname'], lname_len)}   {d['cdate']}\n")
            pre += f"{add_spaces(str(count) + '.  ', l)}   {add_spaces(str(d['uid']), id_len)}   {add_spaces(d['uname'], uname_len)}   {add_spaces(d['fname'], fname_len)}   {add_spaces(d['lname'], lname_len)}   {d['cdate']}\n"
            count += 1

    return JsonResponse({
        'result' : 'success',
        'message' : 'successfully created user list report',
        'data' : {
            'pre' : pre
        } 
    })


def get_files(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    fname_filter = POST.get('filename_filter', '').strip()
    fname_input = POST.get('filename_input', '').strip()
    udate_filter = POST.get('upload_date_filter', '').strip()
    fname_input = PATH + fname_input

    fileuploads = FileUpload.objects.filter(is_archived=False)
    data = []
    fname_len = len('Filename')    

    get_all = POST.get('get_all', '')

    if get_all == 'no':
        if fname_filter != 'none' and fname_input != '':
            if fname_filter == 'starts_with':
                fileuploads = fileuploads.filter(uploaded_file__istartswith=fname_input)
            elif fname_filter == 'ends_with':
                fileuploads = fileuploads.filter(uploaded_file__iendswith=fname_input)
            elif fname_filter == 'contains':
                fileuploads = fileuploads.filter(uploaded_file__icontains=fname_input)
        
        if udate_filter != '':
            fileuploads = fileuploads.filter(upload_date__istartswith=udate_filter)

    if fileuploads.count() == 0:
        return JsonResponse({
            'result' : 'none',
            'message' : 'No files match the filters',
        })

    l = len(str(fileuploads.count() ))

    for fu in fileuploads:
        if len(fu.uploaded_file.name.split('/')[-1]) > fname_len: fname_len = len(fu.uploaded_file.name.split('/')[-1])
        data.append({
            'fid' : fu.id,
            'filename' : fu.uploaded_file.name.split('/')[-1],
            'upload_date' : fu.upload_date
        })
    pre = ''
    with open(f'media/reports/file_list_{id}.txt', 'w') as f:
        f.write('List of files\n\n')
        pre += 'List of files\n\n'
        f.write(f"{add_spaces('    ', l)}   {add_spaces('Filename', fname_len)}   Upload Date\n\n")
        pre += f"{add_spaces('    ', l)}   {add_spaces('Filename', fname_len)}   Upload Date\n\n"
        count = 1
        for d in data:
            f.write(f"{add_spaces(str(count) + '.  ', l)}   {add_spaces(d['filename'], fname_len)}   {d['upload_date']}\n")
            pre += f"{add_spaces(str(count) + '.  ', l)}   {add_spaces(d['filename'], fname_len)}   {d['upload_date']}\n"
            count += 1

        return JsonResponse({
            'result' : 'success',
            'message' : 'successfully created file list report',
            'data' : {
                'pre' : pre
            } 
        })


def get_logs(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    filters = POST.get('filters', '')
    date_filter = POST.get('date_filter', '')

    logs = Log.objects.all().order_by('-log_time')
    
    if filters[0] == 'no':
        filters.pop(0)
        print("=========================")
        print(filters)
        logs = Log.objects.filter(log_code__in=filters).order_by('-log_time')
    
    if date_filter != '':
        logs = logs.filter(log_time__startswith=date_filter)

    if logs.count() == 0:
        return JsonResponse({
            'result' : 'none',
            'message' : 'no activity logs match the filters',
        })
        
    pre = ''
    l = len(str(logs.count()))

    with open(f'media/reports/activity_logs_{id}.txt', 'w') as f:
        f.write('Activity Logs\n\n')
        pre += 'Activity Logs\n\n'
        f.write(f"{add_spaces('Log Time', 35)}   {add_spaces('Activity', 20)}   Log\n\n")
        pre += f"{add_spaces('Log Time', 35)}   {add_spaces('Activity', 20)}   Log\n\n"
        count = 1
        for log in logs:     
            code = ' '.join(log.log_code.capitalize().split('_') )    
            f.write(f"{add_spaces(str(log.log_time) , 35)}   {add_spaces(code, 20)}   {log.log_message}\n")
            pre += f"{add_spaces(str(log.log_time) , 35)}   {add_spaces(code, 20)}   {log.log_message}\n"
            count += 1
        
    return JsonResponse({
        'result' : 'success',
        'message' : 'successfully created activity logs report',
        'data' : {
            'pre' : pre
        } 
    })




#========================== utility functiooowwns ===============

def add_spaces(string, length):
    new_string = string
    while len(new_string) < length:
        new_string += " "
    return new_string

    
    






