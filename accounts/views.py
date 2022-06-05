from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import check_password, make_password
from .models import User
from reports.models import Log
import json
# Create your views here.

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def index(request):
    return render(request, 'accounts/index.html')


def login(request):
    id = request.session.get('user_id', '')
    if id != '':
        return redirect('accounts:profile')
    return render(request, 'accounts/login.html')

def request_login(request):

    if is_ajax(request) and request.method == 'POST':
        POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
        email = POST.get('email', '').strip()
        password = POST.get('password', '').strip()
        if not email or not password:
            return JsonResponse({
                'result' : 'invalid',
                'message' :'fill out empty fields'
            }, status=200)

        user = User.objects.filter(email=email)
        #return JsonResponse({'lastname': user.count})
        if user.count() == 0:
            user = User.objects.filter(username=email)
            if user.count() == 0:
                return JsonResponse({
                    'result': 'invalid',
                    'message': 'invalid credentials no username or email matched'
                    }, status=200)
            elif user.count() == 1:
                if(check_password(password, user[0].password) == True):
                    user = user[0]
                    if user.is_archived:
                        return JsonResponse({
                            'result': 'invalid',
                            'message': 'user is archived'
                        }, status=200)
                    request.session['user_id'] = user.id
                    Log(log_code='login', log_message=f'{user.username} logged in using their username').save()
                    return JsonResponse({
                        'result': 'success',
                        'message': 'logged in using username'
                        }, status=200)
                else:
                    return JsonResponse({
                        'result': 'invalid',
                        'message': 'invalid credentials, invalid password using username'
                        }, status=200)
        elif user.count() == 1:
            if(check_password(password, user[0].password) == True):
                user = user[0]
                if user.is_archived:
                    return JsonResponse({
                        'result': 'invalid',
                        'message': 'user is archived'
                    }, status=200)
                request.session['user_id'] = user.id
                Log(log_code='login', log_message=f'{user.username} logged in using their email').save()
                return JsonResponse({
                        'result': 'success',
                        'message': 'logged in using email'
                        }, status=200)
            else:
                return JsonResponse({
                        'result': 'invalid',
                        'message': 'invalid credentials, invalid password using email'
                        }, status=200)
    else :
        return JsonResponse({
            'result': 'error',
            'message': 'Method is not POST'
            }, status=200)


def register(request):
    id = request.session.get('user_id','')
    if id != '':
        return redirect('accounts:profile')
    return render(request, 'accounts/register.html')


def request_register(request):

    if request.method != 'POST':
        return JsonResponse({'error': 'invalid method'}, status=200)

    email = request.POST.get('email', '').strip()
    username = request.POST.get('username', '').strip()
    firstname = request.POST.get('firstname', '').strip()
    lastname = request.POST.get('lastname', '').strip()
    password = request.POST.get('password', '').strip()
    img = request.FILES.get('file')
    
    if not email or not username or not firstname or not lastname or not password:
        return JsonResponse({
            'result': 'error',
            'message': 'there are empty fields'
            }, status=200)
    else:
        user = User.objects.filter(email=email)
        is_valid = True
        if user.count() != 0:
            is_valid = False
            return JsonResponse({
                'result': 'error',
                'message': 'email already taken'
                }, status=200)
        
        user = User.objects.filter(username=email)
        if user.count() != 0:
            is_valid = False
            return JsonResponse({
                'result': 'error',
                'message': 'username already taken'
                }, status=200)
        
        if is_valid:
            hashed = make_password(password)
            newUser = User(email=email, username=username, first_name=firstname, last_name=lastname, password=hashed)
            if img:
                newUser.profile_image = img
            newUser.save()
            Log(log_code='registration', log_message=f'a new account was registered under the username {newUser.username}').save()
            return JsonResponse({
                'result' : 'success',
                'message': 'successfully registered'
                }, status=200)

def profile(request):
    id = request.session.get('user_id', '')
    if id != '' :
        user = User.objects.get(pk=id)
        context = {'user': user}
        return render(request, 'accounts/profile.html', context)
    else:
        #return render(request, 'accounts/login.html')
        return redirect('accounts:login')

def logout(request):
    id = request.session.get('user_id', '')
    if id != '' :
        user = User.objects.get(pk=id)
        Log(log_code='logout', log_message=f'{user.username} logged out').save()
        del request.session['user_id']
        return redirect('home')

def delete_account(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    user = User.objects.get(pk=id)
    user.is_archived = True
    user.save()
    del request.session['user_id']
    Log(log_code='account_deletion', log_message=f'{user.username} deleted/archived their account').save()
    return JsonResponse({
        'result': 'success',
        'message': 'successfull deleted user'
    }, status=200)

def edit_profile(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    user = User.objects.get(pk=id)
    context = {
        'user' : user
    }
    return render(request, 'accounts/edit_profile.html', context)

def save_profile_changes(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    # POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
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

    user = User.objects.get(pk=id)
    updates = []

    if user.email != email:
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'result': 'invalid',
                'message': 'email is already taken'
            }, status=200)
        user.email = email
        Log(log_code='profile_update', log_message=f'{user.username} updated their email').save()

    if user.username != username:
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'result': 'invalid',
                'message': 'username is already taken'
            }, status=200)
        Log(log_code='profile_update', log_message=f'{user.username} updated their username to {username}').save()
        user.username = username
    
    if user.first_name != firstname:
        Log(log_code='profile_update', log_message=f'{user.username} updated their firstname from {user.first_name} to {firstname}').save()
        user.first_name = firstname

    if user.last_name != lastname:
        user.last_name = lastname
        Log(log_code='profile_update', log_message=f'{user.username} updated their lastname from {user.last_name} to {lastname}').save()


    if img:
        user.profile_image = img
        Log(log_code='profile_update', log_message=f'{user.username} updated their profile image').save()


    user.save()
    return JsonResponse({
        'result': 'success',
        'message': 'successfully updated ' + ', '.join(updates)
    })

def change_password(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    
    user = User.objects.get(pk=id)
    context = {
        'user' : user
    }
    return render(request, 'accounts/change_password.html', context)

def save_new_password(request):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')

    POST = json.loads(request.body.decode('utf-8')) #https://stackoverflow.com/a/67300795/12364598
    current_pass = POST.get('current_pass', '').strip()
    new_pass = POST.get('new_pass', '').strip()
    if current_pass == '':
        return JsonResponse({
            'result': 'invalid',
            'message': 'current password field is empty'
        }, status=200)

    if new_pass == '':
        return JsonResponse({
            'result': 'invalid',
            'message': 'new password field is empty'
        }, status=200)

    user = User.objects.get(pk=id)
    if check_password(current_pass, user.password):
        if current_pass == new_pass:
            return JsonResponse({
                'result': 'invalid',
                'message': 'current password is not allowed:' + current_pass + ":" + new_pass
            }, status=200)

        hashed = make_password(new_pass)
        user.password = hashed
        user.save()
        Log(log_code='profile_update', log_message=f'{user.username} updated their password').save()
        return JsonResponse({
            'result': 'success',
            'message': 'password has been updated'
        }, status=200)
    else:
        return JsonResponse({
            'result': 'invalid',
            'message': 'current password is wrong'
        }, status=200)

    


