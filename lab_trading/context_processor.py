from account.models import TradingScreen

def account(request):

    context_data = dict()
    context_data['trading_screens'] = []
    if request.user.is_authenticated:
        context_data['trading_screens'] = TradingScreen.objects.filter(user=request.user)

    return context_data
