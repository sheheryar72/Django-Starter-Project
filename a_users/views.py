from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from .forms import ProfileForm, EmailForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from allauth.account.utils import send_email_confirmation

def profile_view(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try:
            profile = request.user.profile
        except:
            return redirect('account_login')
    return render(request, 'a_users/profile.html', {'profile': profile})    

@login_required
def profile_edit_view(request):
    print('request.user.profile: ', request.user.profile)
    print('reverse.path: ', request.path)
    print('reverse: ', reverse('profile-onboarding'))

    form = ProfileForm(instance=request.user.profile)

    onboarding = False
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            redirect('profile')

        if request.path == reverse('profile-onboarding'):
            onboarding = True
        else:
            onboarding = False
        
        print('onboarding: ', onboarding)
    return render(request, 'a_users/profile_edit.html', {'form': form, 'onboarding': onboarding})

@login_required
def profile_setting_view(request):
    return render(request, 'a_users/profile_settings.html')

@login_required
def profile_emailchange(request):
    if request.htmx:
        form = EmailForm(instance=request.user)
        return render(request, 'partials/email_form.html', {'form': form})
    
    if request.method == 'POST':
        form = EmailForm(request.POST, instance=request.user)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.warning(request, f'{email} is already in use.')
                return redirect('profile-settings')            

            form.save()

            # Then signals upadte emailaddress and set verified to false

            # Then send confirmation email
            send_email_confirmation(request, request.user)

            return redirect('profile-settings')
        else:
            messages.warning(request, 'Form not valid')
            return redirect('profile-settings')

    return redirect('home')

@login_required
def profile_emailverify(request):
    send_email_confirmation(request, request.user)
    return redirect('profile-settings')

@login_required
def profile_delete_view(request):
    user = request.user
    if request.method == 'POST':
        logout(request)
        user.delete()
        messages.success(request, 'Account deleted what a pity')
        return redirect('home')
    
    return render(request, 'a_users/profile_delete.html')



