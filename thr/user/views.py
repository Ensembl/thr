from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template import RequestContext
from .forms import CustomUserCreationForm


@login_required
def dashboard(request):
    return render(request, 'user/dashboard.html')


def register(request):
    if request.method == 'GET':
        return render(
            request, 'user/register.html',
            {'form': CustomUserCreationForm}
        )
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    return render(request, 'user/register.html', {'form': CustomUserCreationForm}, RequestContext(request))
