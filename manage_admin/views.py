from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from exchange.forms import ExchangeApiForm, CurrencyForm, PairForm, UpdatePairForm
from exchange.models import ExchangeApi, Currency, Pair
from account.forms import TradingScreenForm
from account.models import TradingScreen, User

from django.db.models import Sum

@staff_member_required
def DisplayOverview(request):

    users = User.objects.annotate(test=Sum('currencyamount__amount'))
    
    context = {
        'users' : users
    }
    return render(request, "overview.html", context)

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

        if pair_form.is_valid():
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
        'trading_screen_form': trading_screen_form,
        'exchange_api_form': exchange_api_form,
        'currency_form': currency_form,
        'pair_form': pair_form,
    }
    return render(request, "add_data.html", context)

#DISPLAY VARIABLES 

allowed_class_name = ["exchange_api" , "currency" , "pair" , "trading_screen"]

str_to_class = {
    "exchange_api"      : ExchangeApi,
    "currency"          : Currency,
    "pair"              : Pair, 
    "trading_screen"    : TradingScreen,
}

@staff_member_required
def Display(request, class_name):

    if class_name in allowed_class_name:
        query = str_to_class[class_name].objects.all()
        context = {
            class_name : query,
            "current_class" : class_name,
        }
        return render(request , "display_data.html", context)
    else :
        raise Http404(class_name + " Does not exist")


@staff_member_required
def DisplayOneData(request , class_name , this_pk ):

    if class_name in allowed_class_name:
        
        current_data = str_to_class[class_name].objects.get(pk = this_pk)

        context = {
            class_name : current_data
        }
        return render(request , "display_one_data.html" , context)
    else :
        raise Http404(class_name + " Does not exist")
    

@staff_member_required
def UpdatePair(request, this_pk):

    current_pair = Pair.objects.get(pk=this_pk)
    pair_form = UpdatePairForm(instance = current_pair , initial={'last_updated' : current_pair.last_updated})

    context = {
                "pair_form" : pair_form,
                "current_class" : "pair",
                "current_pk" : current_pair.pk,
            }
    if request.method == 'POST':
        pair_form = UpdatePairForm(request.POST)
        
        if pair_form.is_valid():
            current_pair.currency_1     = Currency.objects.get(pk = request.POST["currency_1"])
            current_pair.currency_2     = Currency.objects.get(pk = request.POST["currency_2"])
            if request.POST.get("active" , "off") == "on":
                current_pair.active = True
            else :
                current_pair.active = False
            current_pair.symbol         = request.POST["symbol"]
            current_pair.save()
            
            pair_form = UpdatePairForm(instance = current_pair ,initial ={'last_updated' : current_pair.last_updated , 'value' : current_pair.value})
            context["pair_form"] = pair_form
            return render(request , "display_one_data.html" , context)

        else : 
            context["pair_form"] = pair_form
            return render(request , "display_one_data.html" , context)

    return render(request , "display_one_data.html" , context)

def Generate_Forms():

    trading_screen_form = TradingScreenForm()
    exchange_api_form = ExchangeApiForm()
    currency_form = CurrencyForm()
    pair_form = PairForm()

    return trading_screen_form , exchange_api_form , currency_form , pair_form