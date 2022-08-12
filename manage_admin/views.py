from django.shortcuts import render, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from exchange.forms import ExchangeForm, ExchangeApiForm, CurrencyForm, PairForm

@staff_member_required
def Create(request):

    exchange_form           = ExchangeForm()
    exchange_api_form       = ExchangeApiForm()
    currency_form           = CurrencyForm()
    pair_form               = PairForm()
    context = {
        'exchange_form'     : exchange_form,
        'exchange_api_form' : exchange_api_form, 
        'currency_form'     : currency_form, 
        'pair_form'         : pair_form,
    }
    return render(request , "add_data.html", context)

def CreateExchange(request):

    if request.method == 'POST':
        current_form = ExchangeForm(request.POST)

        if current_form.is_valid():
            exchange = current_form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        exchange_form           = ExchangeForm()
        exchange_api_form       = ExchangeApiForm()
        currency_form           = CurrencyForm()
        pair_form               = PairForm()
        context = {
            'exchange_form'     : exchange_form,
            'exchange_api_form' : exchange_api_form, 
            'currency_form'     : currency_form, 
            'pair_form'         : pair_form,
        }
        return render(request , "add_data.html", context)


def CreateExchangeAPI(request):
    
    exchange_api_form       = ExchangeApiForm()
    if request.method == 'POST':

        exchange_api_form = ExchangeApiForm(request.POST)

        if exchange_api_form.is_valid():

            exchange = exchange_api_form.save()
            return HttpResponseRedirect('/thanks/')
    
    exchange_form           = ExchangeForm()
    currency_form           = CurrencyForm()
    pair_form               = PairForm()
    context = {
        'exchange_form'     : exchange_form,
        'exchange_api_form' : exchange_api_form, 
        'currency_form'     : currency_form, 
        'pair_form'         : pair_form,
    }
    return render(request , "add_data.html", context)

