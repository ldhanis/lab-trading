from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import Http404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from exchange.forms import ExchangeApiForm, CurrencyForm, PairForm, UpdatePairForm
from exchange.models import ExchangeApi, Currency, Pair
from account.forms import TradingScreenForm
from account.models import CurrencyAmount, TradingScreen, User, Order
from account.tables import OrderTable,CurrencyTable

from manage_admin.forms import *

from lab_trading import misc_kraken
from datetime import timedelta
import datetime as date

def DisplayOrders(request, trading_screen):

    
    order_table = OrderTable(Order.objects.all())

    return render(request, "overview.html" , context) 

def DisplayOverview(request, trading_screen):

    trade  = TradingScreen.objects.get(pk=trading_screen)

    
    #recupération des dernieres valeurs du portefeuille. 
    
    labels=[]
    data = [0,1,2]
    labels_doughnut=[]
    doughnut=[]
    format = '%Y/%m/%d %H:%M:%S';

    usd = Currency.objects.get(name = "USD")

    actual_portfolio_value =0
    for currency_amount in trade.currency_amounts.all():
        currency_1_pk = currency_amount.currency.pk
        try:
            pair = Pair.objects.filter(currency_1 =currency_1_pk).get(currency_2 = Currency.objects.get(name = "USD"))
            pair_value = pair.value
            labels_doughnut.append(currency_amount.currency.name)
            doughnut.append(currency_amount.amount*pair_value)
            actual_portfolio_value += currency_amount.amount*pair_value
        except:
            print("pair not found")
   
    print(actual_portfolio_value)

    orders = Order.objects.filter(trading_screen=trade).order_by('-created_on')

    for order in orders:
        portfolio_value = 0
        labels.append(date.datetime.strftime(order.created_on, format))
        current_pair = order.pair



    date_form = DateForm()
    currency_table = CurrencyTable(trade.currency_amounts.all())
    currency_table.paginate(page=request.GET.get("page", 1), per_page=10)
    order_table = OrderTable(Order.objects.all())
    order_table.paginate(page=request.GET.get("page", 1), per_page=10)


    #repartition des currency

    trader_infos = trade.user

    context = {
        'date_form' : date_form, 
        'order_table' : order_table,
        'currency_table' : currency_table,
        'portfolio_value':portfolio_value,
        'labels' : labels,
        'data' : data,
        'doughnut_data' : doughnut,
        'labels_doughnut' : labels_doughnut,
        'actual_portfolio_value' : actual_portfolio_value,
        'trader_infos' : trader_infos,
    }
    
    return render(request, "overview.html" , context)

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