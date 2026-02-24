from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm
from .models import Profile, AVATAR_CHOICES


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'✅ Аккаунт успешно создан! Добро пожаловать, {user.username}!')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {
        'form': form,
        'avatar_choices': AVATAR_CHOICES,
    })


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        avatar = request.POST.get('avatar')
        bio = request.POST.get('bio', '')
        if avatar:
            profile.avatar = avatar
        profile.bio = bio
        profile.save()
        messages.success(request, '✅ Профиль успешно обновлён!')
        return redirect('profile')

    context = {
        'profile': profile,
        'avatar_choices': AVATAR_CHOICES,
    }
    return render(request, 'register/profile.html', context)
