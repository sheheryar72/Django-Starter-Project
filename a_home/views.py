from django.shortcuts import render

def homw_view(request):
    return render(request, 'home.html')
