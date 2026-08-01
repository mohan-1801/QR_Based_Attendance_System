from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .forms import LoginForm, UserProfileForm, ForgotPasswordForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is None and '@' in username:
                # Try finding by email
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    u = User.objects.get(email=username)
                    user = authenticate(request, username=u.username, password=password)
                except User.DoesNotExist:
                    pass

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.get_full_name_or_username()}!")
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('dashboard:dashboard')
                else:
                    messages.error(request, "Account is disabled. Contact system administrator.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'accounts/profile.html', {'form': form, 'user_obj': user})

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Your password was changed successfully!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            messages.success(request, f"Password reset instructions sent to {email}. (Check console for email backend output).")
            return redirect('accounts:login')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})
