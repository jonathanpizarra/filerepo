from django.http import HttpResponse
from django.shortcuts import render, redirect


def home(request):
    print("=================home==============")
    return render(request, 'filerepo/home.html')

def file(request, filename):
    id = request.session.get('user_id', '')
    if id == '':
        return redirect('accounts:login')
    else:
        return HttpResponse('not workinggggg')




