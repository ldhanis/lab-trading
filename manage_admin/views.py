from django.shortcuts import render, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from exchange.forms import ExchangeApiForm, CurrencyForm, PairForm
from account.forms import TradingScreenForm


@staff_member_required
def Create(request):
    trading_screen_form = TradingScreenForm()
    exchange_api_form = ExchangeApiForm()
    currency_form = CurrencyForm()
    pair_form = PairForm()
    context = {
        'trading_screen_form': trading_screen_form,
        'exchange_api_form': exchange_api_form,
        'currency_form': currency_form,
        'pair_form': pair_form,
    }
    return render(request, "add_data.html", context)


@staff_member_required
def CreateExchangeAPI(request):

    exchange_api_form = ExchangeApiForm()
    if request.method == 'POST':

        exchange_api_form = ExchangeApiForm(request.POST)

        if exchange_api_form.is_valid():

            exchange_api_form.save()
            return HttpResponseRedirect('/thanks/')

    trading_screen_form = TradingScreenForm()
    currency_form = CurrencyForm()
    pair_form = PairForm()
    context = {
        'trading_screen_form': trading_screen_form,
        'exchange_api_form': exchange_api_form,
        'currency_form': currency_form,
        'pair_form': pair_form,
    }
    return render(request, "add_data.html", context)


@staff_member_required
def CreateCurrency(request):

    currency_form = CurrencyForm()
    if request.method == 'POST':

        currency_form = CurrencyForm(request.POST)

        if currency_form.is_valid():

            currency_form.save()
            return HttpResponseRedirect('/thanks/')

    trading_screen_form = TradingScreenForm()
    exchange_api_form = ExchangeApiForm()
    pair_form = PairForm()
    context = {
        'trading_screen_form': trading_screen_form,
        'exchange_api_form': exchange_api_form,
        'currency_form': currency_form,
        'pair_form': pair_form,
    }
    return render(request, "add_data.html", context)


@staff_member_required
def CreatePair(request):

    pair_form = PairForm()
    if request.method == 'POST':

        pair_form = PairForm(request.POST)

        print("post")
        if pair_form.is_valid():
            print("is_Valid")
            pair_form.save()
            return HttpResponseRedirect('/thanks/')

    trading_screen_form = TradingScreenForm()
    exchange_api_form = ExchangeApiForm()
    currency_form = CurrencyForm()
    context = {
        'trading_screen_form': trading_screen_form,
        'exchange_api_form': exchange_api_form,
        'currency_form': currency_form,
        'pair_form': pair_form,
    }
    return render(request, "add_data.html", context)


@staff_member_required
def CreateTradingScreen(request):

    trading_screen_form = TradingScreenForm()
    if request.method == 'POST':

        trading_screen_form = TradingScreenForm(request.POST)

        if trading_screen_form.is_valid():
            trading_screen_form.save()
            return HttpResponseRedirect('/thanks/')

    exchange_api_form = ExchangeApiForm()
    currency_form = CurrencyForm()
    pair_form = PairForm()
    context = {
        'exchange_api_form': exchange_api_form,
        'currency_form': currency_form,
        'pair_form': pair_form,
    }
    return render(request, "add_data.html", context)
