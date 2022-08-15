from django.shortcuts import render, redirect, get_object_or_404
from account.forms import UserLoginForm, CustomUserCreationForm

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.http import url_has_allowed_host_and_scheme

from lab_trading import settings

from account.models import *
from exchange.models import *

# Create your views here.


def redirect_after_login(request):
    nxt = request.GET.get("next", None)
    if nxt is None:
        return redirect(settings.LOGIN_REDIRECT_URL)
    elif not url_has_allowed_host_and_scheme(
            url=nxt,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure()):
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return redirect(nxt)


def user_login(request):

    login_form = UserLoginForm(request.POST or None)

    if login_form.is_valid():
        user = login_form.login(request)
        login(request, user)
        print('User logged in')
        return redirect_after_login(request)

    context = {
        'login_form': login_form
    }

    return render(request, 'login.html', context)


def user_register(request):

    account_form = CustomUserCreationForm(request.POST or None)

    if request.method == 'POST':
        if request.user.is_authenticated:
            messages.warning(request, _("Vous êtes déjà connecté.e"))

        if User.objects.filter(email__iexact=request.POST.get('email')).first():
            messages.warning(request, _(
                "Cette addresse email est déjà utilisée"))

        elif account_form.is_valid():
            user = account_form.save()
            login(request, user)
            return redirect_after_login(request)

        else:
            messages.warning(request, _(
                "Une erreur s'est produite lors de votre inscription, veuillez réessayer"))

    context = {
        'account_form': account_form,
    }

    return render(request, 'register.html', context)


def user_logout(request):
    logout(request)
    return redirect('login_page')

