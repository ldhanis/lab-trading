from django import forms 

class DateForm(forms.Form):

    date_from = forms.DateField(
        widget=forms.TextInput(     
            attrs={'type': 'date'} 
        )
    )
    date_to = forms.DateField(
        widget=forms.TextInput(     
            attrs={'type': 'date'} 
        )
    )