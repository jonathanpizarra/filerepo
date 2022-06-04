from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Category, FileUpload
from accounts.models import User
from reports.models import Log
import json
import os
from django.core import serializers
from django.contrib.auth.hashers import check_password, make_password
# Create your views here.

# not allowed for filename === \ / : * ? " < > |

not_allowed = ('\\', '/', ':', '*', '?', '"', '<', '>', '|')

def index(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    user = get_object_or_404(User, pk=id)
    categories = Category.objects.filter(is_archived=False)
    fileuploads = FileUpload.objects.filter(is_archived=False).order_by('-upload_date')
    files = []
    for fus in fileuploads:
        files.append({
            'file_id' : fus.id,
            'filename' : fus.uploaded_file.name.split('/')[-1],
            'filesize' : fus.uploaded_file.size,
            'filepath' : fus.uploaded_file.url,
            'category' : fus.category.name,
            'uploader' : fus.uploader.username,
            'upload_date' : fus.upload_date.strftime("%m/%d/%Y, %H:%M:%S"),
        })
    context = {
        'categories': categories,
        'user': user,
        'fileuploads': fileuploads,
        'files' : files,
        'uploaders' : FileUpload.objects.values_list('uploader__username', flat=True).distinct()
    }
    return render(request, 'file_manager/index.html', context)

def upload_file(request):
    id = request.session.get('user_id','')
    if id == '':
        return redirect('accounts:login')
    
    fileupload = request.FILES.get('file', '')
    category_id = request.POST.get('category_id')
    filename = request.POST.get('filename', '')

    if not fileupload:
        return JsonResponse({
            'result': 'invalid',
            'message': 'no file found' 
        }, status=200)
    
    if category_id == 'none':
        return JsonResponse({
            'result': 'invalid',
            'message': 'no category selected' 
        }, status=200)
    
    if filename == '':
        return JsonResponse({
            'result': 'invalid',
            'message': 'no filename indicated' 
        }, status=200)

    if any(na in filename for na in not_allowed) :
        return JsonResponse({
            'result': 'invalid',
            'message': 'A file name can\'t contain the following characters:\n\n \\ / : * ? " < > |' 
        }, status=200)

    categ = Category.objects.filter(pk=category_id, is_archived=False)
    if categ.count() == 0:
        return JsonResponse({
            'result': 'invalid',
            'message': 'invalid category' 
        }, status=200)

    user = get_object_or_404(User, pk=id)
    ext = fileupload.name.split('.')[-1]
    filename_copy = 'files/' + filename + '.' + ext
    count = 0
    filtered = FileUpload.objects.filter(uploaded_file=filename_copy).count()
    while filtered > 0:
        count += 1
        filename_copy = 'files/' + filename + '_' + str(count) + '.' + ext
        filtered = FileUpload.objects.filter(uploaded_file=filename_copy).count()
        print("==============", filtered, filename_copy)
    
    if count > 0:
        filename = filename + '_' + str(count) + '.' + ext
    else :
        filename = filename + '.' + ext

    newFile = FileUpload(category=categ.first(), uploader=user, last_editor=user, uploaded_file=fileupload)
    newFile.uploaded_file.name = filename 
    newFile.save()

    fileuploads = FileUpload.objects.filter(is_archived=False).order_by('-upload_date')
    files = []
    for fus in fileuploads:
        files.append({
            'file_id' : fus.id,
            'filename' : fus.uploaded_file.name.split('/')[-1],
            'filesize' : fus.uploaded_file.size,
            'filepath' : fus.uploaded_file.url,
            'category' : fus.category.name,
            'uploader' : fus.uploader.username,
            'upload_date' : fus.upload_date.strftime("%m/%d/%Y, %H:%M:%S"),
        })
    
    Log(log_code='file_upload', log_message=f'{user.username} uploaded a new file {filename}').save()
    return JsonResponse({
        "result" : "success",
        "message" : "successfully uploaded file",
        "data" : {
            'files' : files
        }
    })
    

def admin_categories(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    user = get_object_or_404(User, pk=id)
    if user.is_admin:
        categories = Category.objects.filter(is_archived=False).order_by('-creation_date')
        user = get_object_or_404(User, pk=id)
        context = {
            'categories': categories,
            'user': user
        }
        return render(request, 'file_manager/admin_categories.html', context)
    else:
        return redirect('accounts:profile')

def save_category_changes(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    user = get_object_or_404(User, pk=id)
    if user.is_admin:
        POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
        category_id = POST.get('category_id', '').strip()
        name = POST.get('name', '').strip()
        description = POST.get('description', '').strip()

        if not category_id or not name or not description:
            return JsonResponse({
                'result' : 'invalid',
                'message' : 'fill out empty fields'
            }, status=200)

        category = get_object_or_404(Category, pk=category_id)
        if name != category.name:
            Log(log_code='category_edit', log_message=f'{user.username} changed category name {category.name} to {name}').save()
            category.name = name
        
        if description != category.description:
            Log(log_code='category_edit', log_message=f'{user.username} changed category description of {category.name}').save()
            category.description = description
        
        category.last_editor= user
        category.save()
        return JsonResponse({
            'result' : 'success',
            'message': 'successfully updated category'
        }, status=200)
    else:
        return redirect('accounts:profile')

def delete_selected_categories(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    user = get_object_or_404(User, pk=id)
    if not user.is_admin:
        return redirect('accounts:profile')

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    category_ids = POST.get('category_ids', '')
    for cid in category_ids:
        c = get_object_or_404(Category, pk=cid)
        files = FileUpload.objects.filter(category=c)
        for f in files:
            f.is_archived = True
            f.save()
        c.is_archived = True
        c.save()
        Log(log_code='category_deletion', log_message=f'{user.username} deleted/archived the category {c.name}').save()

    return JsonResponse({
        'result' : 'success',
        'message' : 'successfully deleted selected categories',
        'data' : {
            'count' : Category.objects.filter(is_archived=False).count()
        }
    })

def admin_save_new_category(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    user = get_object_or_404(User, pk=id)
    if not user.is_admin:
        return redirect('accounts:profile')

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    name = POST.get('name', '').strip()
    desc = POST.get('desc', '').strip()

    if not name or not desc:
        return JsonResponse({
            'result': 'invalid',
            'message' : 'emty fields'
        },status=200)

    newCategory = Category(name=name, description=desc, creator=user, last_editor=user)
    newCategory.save()
    Log(log_code='category_creation', log_message=f'{user.username} created new category {newCategory.name}').save()
    return JsonResponse({
            'result': 'success',
            'message' : 'success creating new category ' + name,
            'data' : {
                'id' : newCategory.id,
                'name' : newCategory.name,
                'desc' : newCategory.description,
                'count' : Category.objects.filter(is_archived=False).count()

            }

        },status=200)

def admin_get_category_details(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    user = get_object_or_404(User, pk=id)
    if not user.is_admin:
        return redirect('accounts:profile')

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    id = POST.get('category_id', '')
    category = get_object_or_404(Category, pk=id)

    if category:
        category.creator.password = ''
        category.last_editor.password = ''
        ca = serializers.serialize('json', [category])
        cr = serializers.serialize('json', [category.creator])
        ed = serializers.serialize('json', [category.last_editor])
        num = FileUpload.objects.filter(category=category, is_archived=False).count()
        return JsonResponse({
            'result' : 'success',
            'message' : 'successfully fetched category data',
            'data' : {
                'category' : ca,
                'creator' : cr,
                'editor' : ed,
                'count' : num
            }
        }, status=200)

def admin_users(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    user = get_object_or_404(User, pk=id)
    if not user.is_admin:
        return redirect('accounts:profile')
    
    users = User.objects.filter(is_admin=False, is_archived=False).order_by('-creation_date')
    context = {
        'users' : users,
        'user' : user
    }
    return render(request, 'file_manager/admin_users.html', context)

def admin_save_profile_changes(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    user = get_object_or_404(User, pk=id)
    admin = get_object_or_404(User, pk=id)
    if not user.is_admin:
        return render('accounts:profile')
    
    user_id = request.POST.get('user_id', '')
    email = request.POST.get('email', '')
    username = request.POST.get('username', '')
    firstname = request.POST.get('firstname', '')
    lastname = request.POST.get('lastname', '')
    img = request.FILES.get('file')

    if not email or not username or not firstname or not lastname:
        return JsonResponse({
            'result' : 'error',
            'message': 'there are empty fields'
            }, status=200)

    user = User.objects.get(pk=user_id)
    updates = []

    if user.email != email:
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'result': 'invalid',
                'message': 'email is already taken'
            }, status=200)
        Log(log_code='profile_update', log_message=f'{admin.username} changed the email of user {user.username}').save()
        user.email = email

    if user.username != username:
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'result': 'invalid',
                'message': 'username is already taken'
            }, status=200)
        Log(log_code='profile_update', log_message=f'{admin.username} changed the username of {user.username} to username').save()
        user.username = username
        
    
    if user.first_name != firstname:
        Log(log_code='profile_update', log_message=f'{admin.username} changed the firstname of {user.username} from {user.first_name} to {firstname}').save()
        user.first_name = firstname

    if user.last_name != lastname:
        Log(log_code='profile_update', log_message=f'{admin.username} changed the lastname of {user.username} from {user.last_name} to {lastname}').save()
        user.last_name = lastname

    if img:
        user.profile_image = img
        Log(log_code='profile_update', log_message=f'{admin.username} updated the profile image of {user.username}').save()

    user.save()
    return JsonResponse({
        'result': 'success',
        'message': 'successfully updated ' + ', '.join(updates),
        'data' : {
            'path' : user.profile_image.url
        }
    })

def admin_add_user(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    user = get_object_or_404(User, pk=id)
    admin = get_object_or_404(User, pk=id)
    if not user.is_admin:
        return render('accounts:profile')

    email = request.POST.get('email', '')
    username = request.POST.get('username', '')
    firstname = request.POST.get('firstname', '')
    lastname = request.POST.get('lastname', '')
    password = request.POST.get('password', '')
    img = request.FILES.get('file')

    if not email or not username or not firstname or not lastname or not password:
        return JsonResponse({
            'result' : 'error',
            'message': 'there are empty fields'
            }, status=200)

    user = User.objects.filter(username=username, is_archived=False)
    if user.count() >= 1:
        return JsonResponse({
            'result' : 'error',
            'message': 'username already taken'
            }, status=200)

    user = User.objects.filter(email=email, is_archived=False)
    if user.count() >= 1:
        return JsonResponse({
            'result' : 'error',
            'message': 'email already taken'
            }, status=200)

    hashed = make_password(password)
    newUser = User(email=email, username=username, first_name=firstname, last_name=lastname, password=hashed)
    newUser.save()

    newUser.password = ''
    user = serializers.serialize('json', [newUser])
    Log(log_code='registration', log_message=f'{admin.username} created a new account with username {user.username}').save()
    return JsonResponse({
            'result' : 'success',
            'message': 'successfully added new user',
            'data' : {
                'user' : user,
                'count' : User.objects.filter(is_archived=False).count()
                }
            }, status=200)
    
def admin_get_user_details(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    user = get_object_or_404(User, pk=id)
    if not user.is_admin:
        return render('accounts:profile')

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    user_id = POST.get('user_id')
    user = User.objects.filter(pk=user_id, is_archived=False)
    if user.count() == 0:
        return JsonResponse({
            'result' : 'error',
            'message': 'user id not found'
        })

    user.password = ''
    u = serializers.serialize('json', user)
    return JsonResponse({
        'result' : 'success',
        'message': 'successfully fetch user details',
        'data' : {
            'user' : u,
            'count' : FileUpload.objects.filter(uploader=user.first(), is_archived=False).count()
        }
    })
    
def admin_delete_selected_users(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    user = get_object_or_404(User, pk=id)
    if not user.is_admin:
        return render('accounts:profile')

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    user_ids = POST.get('user_ids', '')
    for uid in user_ids:
        u = get_object_or_404(User, pk=uid)
        u.is_archived = True
        u.save()
        Log(log_code='profile_deletion', log_message=f'{user.username} deleted/archived user {u.username}').save()
    
    return JsonResponse({
        'result' : 'success',
        'message': 'successfully deleted/archived selected users',
        'data' : {
            'count' : User.objects.filter(is_archived=False).count()
        }
    })

def delete_selected_files(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    user = get_object_or_404(User, pk=id)
    
    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    file_ids = POST.get('file_ids', '')

    if file_ids == '':
        return JsonResponse({
            'result' : 'invalid',
            'message': 'no file ids found'
        })

    for fid in file_ids:
        f = get_object_or_404(FileUpload, pk=fid, is_archived=False)
        f.is_archived = True
        f.save()
        fname = f.uploaded_file.name.split('/')[-1]
        Log(log_code='file_deletion', log_message=f'{user.username} deleted/archived the file {fname}').save()

    fileuploads = FileUpload.objects.filter(is_archived=False).order_by('-upload_date')
    files = []
    for fus in fileuploads:
        files.append({
            'file_id' : fus.id,
            'filename' : fus.uploaded_file.name.split('/')[-1],
            'filesize' : fus.uploaded_file.size,
            'filepath' : fus.uploaded_file.url,
            'category' : fus.category.name,
            'uploader' : fus.uploader.username,
            'upload_date' : fus.upload_date.strftime("%m/%d/%Y, %H:%M:%S"),
        })
    
    return JsonResponse({
        "result" : "success",
        "message" : "successfully deleted/archived selected files",
        "data" : {
            'files' : files
        }
    })


    # mali to
    return JsonResponse({
        'result' : 'success',
        'message': 'successfully deleted/archived selected files',
        'data' : {
            'count' : FileUpload.objects.filter(is_archived=False).count()
        }
    })

def get_file_details(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    file_id = POST.get('file_id', '')
    if file_id == '':
        return JsonResponse({
            'result' : 'invalid',
            'message': 'no file id found'
        })
    
    fileupload = get_object_or_404(FileUpload, pk=file_id)
    uploader = fileupload.uploader
    updater = fileupload.last_editor
    category = fileupload.category
    fu = serializers.serialize('json', [fileupload])
    ul = serializers.serialize('json', [uploader])
    ud = serializers.serialize('json', [updater])
    ca = serializers.serialize('json', [category])
    return JsonResponse({
        'result' : 'success',
        'message': 'file found',
        'data' : {
            'fileupload' : fu,
            'uploader': ul,
            'updater' : ud,
            'category' : ca,
            'filesize' : fileupload.uploaded_file.size,
            'path' : fileupload.uploaded_file.path
        }
    })

def save_file_changes(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    user = get_object_or_404(User, pk=id)
    
    file_id = request.POST.get('file_id', '')
    filename = request.POST.get('filename', '')
    category_id = request.POST.get('category_id', '')
    description = request.POST.get('description', '')
    fileupload = request.FILES.get('fileupload', '')

    if file_id == '':
        return JsonResponse({
            'result' : 'invalid',
            'message': 'no file id found'
        })

    if filename == '':
        return JsonResponse({
            'result' : 'invalid',
            'message': 'no filename found'
        })

    file_match = get_object_or_404(FileUpload, pk=file_id)
    category = get_object_or_404(Category, pk=category_id)
    ext = ''
    if fileupload == '':
        ext = file_match.uploaded_file.name.split('.')[-1]
    else :
        ext = fileupload.name.split('.')[-1]
    
    filename_copy = 'files/' + filename + '.' + ext
    count = 0
    filtered = FileUpload.objects.filter(uploaded_file=filename_copy).exclude(pk=file_id).count()
    while filtered > 0:
        count += 1
        filename_copy = 'files/' + filename + '_' + str(count) + '.' + ext
        filtered = FileUpload.objects.filter(uploaded_file=filename_copy).count()
        print("==============", filtered, filename_copy)
    
    if count > 0:
        filename = filename + '_' + str(count) + '.' + ext
    else :
        filename = filename + '.' + ext

    if file_match.description != description:
        file_match.description = description
        Log(log_code='file_edit', log_message=f'{user.username} updated the description of file {filename.split("/")[-1]}').save()

    if file_match.category != category:
        Log(log_code='file_edit', log_message=f'{user.username} updated the category of file {filename.split("/")[-1]} from {file_match.category} to {category}').save()
        file_match.category = category

    if fileupload :
        path = file_match.uploaded_file.path
        file_match.uploaded_file = fileupload
        file_match.save()
        Log(log_code='file_edit', log_message=f'{user.username} replaced the file {filename}').save()
        if os.path.isfile(path):
            os.remove(path)
    file_match.rename(filename)
    file_match.save()
    fu = serializers.serialize('json', [file_match])
    categ = serializers.serialize('json', [category])
    up = serializers.serialize('json', [file_match.uploader])

    return JsonResponse({
            'result' : 'success',
            'message': 'file updated',
            'data' : {
                'filesize' : file_match.uploaded_file.size,
                'filepath' : file_match.uploaded_file.path,
                'fileupload' : fu,
                'category' : categ,
                'uploader' : up
            }
        })

def file_view(request, file_id):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    fileupload = get_object_or_404(FileUpload, pk=file_id)

    context = {
        'file' : fileupload
    }

    return render(request, 'file_manager/file_view.html', context)

def archives(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    user = get_object_or_404(User, pk=id)

    file_archives = FileUpload.objects.filter(is_archived=True).order_by('-upload_date')
    category_archives = Category.objects.filter(is_archived=True)
    user_archives = User.objects.filter(is_archived=True).exclude(pk=user.id)
    context = {}
    if user.is_admin:
        context = {
            'user' : user,
            'file_archives' : file_archives,
            'category_archives' : category_archives,
            'user_archives' : user_archives
        }
    else :
        context = {
            'user' : user,
            'file_archives' : file_archives
        }
    
    return render(request, 'file_manager/archives.html', context)

def restore_selected_files(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    user = get_object_or_404(User, pk=id)

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    file_ids = POST.get('file_ids', '')
    if file_ids == '':
        return JsonResponse({
            "result" : "invalid",
            "message" : "no file ids found"
        })
    
    for fid in file_ids:
        f = get_object_or_404(FileUpload, pk=fid)
        f.is_archived = False
        f.save()
        Log(log_code='file_restore', log_message=f'{user.username} restored the file {f.uploaded_file.name.split("/")[-1]} from archives').save()
    
    fileuploads = FileUpload.objects.filter(is_archived=True).order_by('-upload_date')
    files = []
    for fus in fileuploads:
        files.append({
            'file_id' : fus.id,
            'filename' : fus.uploaded_file.name.split('/')[-1],
            'filesize' : fus.uploaded_file.size,
            'filepath' : fus.uploaded_file.url,
            'category' : fus.category.name,
            'uploader' : fus.uploader.username,
            'upload_date' : fus.upload_date.strftime("%m/%d/%Y, %H:%M:%S"),
        })
    
    return JsonResponse({
        "result" : "success",
        "message" : "successfully restored selected files",
        "data" : {
            'archived_files' : files
        }
    })
    
def restore_selected_users(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    user = get_object_or_404(User, pk=id)

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    user_ids = POST.get('user_ids', '')
    if user_ids == '':
        return JsonResponse({
            "result" : "invalid",
            "message" : "no user ids found"
        })
    
    for uid in user_ids:
        u = get_object_or_404(User, pk=uid)
        u.is_archived = False
        u.save()
        Log(log_code='account_restore', log_message=f'{user.username} restored the account with username {u.username}').save()
    
    archived_users = User.objects.filter(is_archived=True)
    users = []
    for u in archived_users:
        users.append({
            'user_id' : u.id,
            'username' : u.username,
            'firstname' : u.first_name,
            'lastname' : u.last_name,
            'email' : u.email
        })
    
    return JsonResponse({
        "result" : "success",
        "message" : "successfully restored selected users",
        "data" : {
            'archived_users' : users
        }
    })
  
def restore_selected_categories(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    user = get_object_or_404(User, pk=id)

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    category_ids = POST.get('category_ids', '')
    if category_ids == '':
        return JsonResponse({
            "result" : "invalid",
            "message" : "no category ids found"
        })
    
    for cid in category_ids:
        c = get_object_or_404(Category, pk=cid)
        c.is_archived = False
        c.save()
        fs = FileUpload.objects.filter(category=c)
        for f in fs:
            f.is_archived = False
            f.save()
        Log(log_code='category_restore', log_message=f'{user.username} restored the category {c.name} from the archives together with its files').save()
    
    archived_categories = Category.objects.filter(is_archived=True)
    categories = []
    for c in archived_categories:
        categories.append({
            'category_id' : c.id,
            'name' : c.name,
            'description': c.description
        })
    
    return JsonResponse({
        "result" : "success",
        "message" : "successfully restored selected categoriess",
        "data" : {
            'archived_categories' : categories
        }
    })

# discontinued............ sa front end na lang ifilter???
def filter_files(request):

    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    filename_filter = POST.get('filename_filter').strip()
    filename_input = POST.get('filename_input').strip()
    category_filter = POST.get('category_filter').strip()
    uploader_filter = POST.get('uploader_filter').strip()
    date_filter = POST.get('date_filter').strip()

    files = FileUpload.objects.filter(is_archived=False)
    if (filename_filter != 'none' and filename_input != '') :
        filename_input = 'files/' + filename_input
        if filename_filter == 'starts_with':
            files = FileUpload.objects.filter(is_archived=False, upload_file__istartswith=filename_input)
    
    return JsonResponse({
        'result' : 'success',
        'message' : 'try',
        'data' : {
            'date' : date_filter,
            'files' : serializers.serialize('json', files )
        }
    })

















