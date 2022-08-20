from django.shortcuts import render, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from exchange.forms import ExchangeApiForm, CurrencyForm, PairForm
from exchange.models import ExchangeApi, Currency, Pair
from account.forms import TradingScreenForm
from account.models import TradingScreen


@staff_member_required
def Create(request):
    trading_screen_form , exchange_api_form , currency_form , pair_form= Generate_Forms()
    context = {
        'trading_screen_form': trading_screen_form,
        'exchange_api_form': exchange_api_form,
        'currency_form': currency_form,
        'pair_form': pair_form,
    }
    return render(request, "add_data.html", context)


@staff_member_required
def CreateExchangeAPI(request):

    trading_screen_form , exchange_api_form , currency_form , pair_form= Generate_Forms()
    if request.method == 'POST':

        exchange_api_form = ExchangeApiForm(request.POST)

        if exchange_api_form.is_valid():

            exchange_api_form.save()
            return HttpResponseRedirect('/thanks/')

    context = {
        'trading_screen_form': trading_screen_form,
        'exchange_api_form': exchange_api_form,
        'currency_form': currency_form,
        'pair_form': pair_form,
    }
    return render(request, "add_data.html", context)


@staff_member_required
def CreateCurrency(request):

    trading_screen_form , exchange_api_form , currency_form , pair_form = Generate_Forms()

    if request.method == 'POST':

        currency_form = CurrencyForm(request.POST)

        if currency_form.is_valid():

            currency_form.save()
            return HttpResponseRedirect('/thanks/')

    context = {
        'trading_screen_form': trading_screen_form,
        'exchange_api_form': exchange_api_form,
        'currency_form': currency_form,
        'pair_form': pair_form,
    }
    return render(request, "add_data.html", context)


@staff_member_required
def CreatePair(request):

    trading_screen_form , exchange_api_form , currency_form , pair_form= Generate_Forms()
    if request.method == 'POST':

        pair_form = PairForm(request.POST)

        print("post")
        if pair_form.is_valid():
            print("is_Valid")
            pair_form.save()
            return HttpResponseRedirect('/thanks/')

    context = {
        'trading_screen_form': trading_screen_form,
        'exchange_api_form': exchange_api_form,
        'currency_form': currency_form,
        'pair_form': pair_form,
    }
    return render(request, "add_data.html", context)


@staff_member_required
def CreateTradingScreen(request):

    trading_screen_form , exchange_api_form , currency_form , pair_form= Generate_Forms()
    if request.method == 'POST':

        trading_screen_form = TradingScreenForm(request.POST)

        if trading_screen_form.is_valid():
            trading_screen_form.save()
            return HttpResponseRedirect('/thanks/')

    context = {
        'exchange_api_form': exchange_api_form,
        'currency_form': currency_form,
        'pair_form': pair_form,
    }
    return render(request, "add_data.html", context)

def Display(request, class_name):

    allowed_class_name = ["exchange_api" , "currency" , "pair" , "trading_screen"]

    str_to_class = {
        "exchange_api"      : ExchangeApi,
        "currency"          : Currency,
        "pair"              : Pair, 
        "trading_screen"    : TradingScreen,
    }
    if class_name in allowed_class_name:
        query = str_to_class[class_name].objects.all()
        context = {
            class_name : query,
        }
        print(query.count)
        return render(request , "display_data.html", context)
    else :
        raise Http404(class_name + " Does not exist")

def Generate_Forms():

    trading_screen_form = TradingScreenForm()
    exchange_api_form = ExchangeApiForm()
    currency_form = CurrencyForm()
    pair_form = PairForm()

    return trading_screen_form , exchange_api_form , currency_form , pair_form