from django.shortcuts import render, redirect
from exchange.models import *

# List assets owned by the user
# Display pairs
def user_dashboard(request):

	if not request.user.is_authenticated:
		return redirect('login_page')

	context = {'pairs' : Pair.objects.filter(active=True)}

	return render(request, 'display_pairs.html', context)
