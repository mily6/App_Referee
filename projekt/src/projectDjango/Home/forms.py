from django.contrib.auth.models import User
from .models import RefereeAvailability
from django import forms
from datetime import date
from .models import Message, Referee, Match, Team
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import PasswordChangeForm
'''
class SedziaRegistrationForm(UserCreationForm):
    imie = forms.CharField(max_length=100, required=True)
    nazwisko = forms.CharField(max_length=100, required=True)
    adres_zamieszkania = forms.CharField(max_length=100, required=True)
    nr_telefonu = forms.CharField(max_length=15, required=True)
    data_urodzenia = forms.DateField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'imie', 'nazwisko', 'adres_zamieszkania', 'nr_telefonu', 'data_urodzenia']
'''

class RefereeAvailabilityForm(forms.ModelForm):
    vacation = forms.BooleanField(label="Urlop", required=False)
    date = forms.DateField(label="Data", widget=forms.DateInput(attrs={"type": "date"}))
    time_start = forms.TimeField(label="Możliwa godzina rozpoczęcia sędziowania", widget=forms.TimeInput(attrs={"type": "time"}))
    time_finish = forms.TimeField(label="Możliwa godzina zakończenia sędziowania", widget=forms.TimeInput(attrs={"type": "time"}))
    possible_distance_match = forms.IntegerField(label="Możliwa odległość [km]", widget=forms.NumberInput(attrs={"min": "0"}))
    number_of_matches = forms.IntegerField(label="Możliwa ilość meczów", widget=forms.NumberInput(attrs={"min": "0"}))

    class Meta:
        model = RefereeAvailability
        fields = ("date", "number_of_matches", "possible_distance_match", "time_start", "time_finish")

    def clean_date(self):
        data = self.cleaned_data['date']
        if data <= date.today():
            raise forms.ValidationError("Data musi być przyszła!")
        return data

    def clean(self):
        cleaned_data = super().clean()

        godzina_rozpoczecia = cleaned_data.get('time_start')
        godzina_zakonczenia = cleaned_data.get('time_finish')

        if godzina_rozpoczecia and godzina_zakonczenia:
            if godzina_rozpoczecia >= godzina_zakonczenia:
                msg = "Godzina rozpoczęcia musi być wcześniejsza niż godzina zakończenia."
                self.add_error('time_finish', msg)

        return cleaned_data

class MessageForm(forms.ModelForm):
    subject = forms.CharField(widget=forms.TextInput(attrs={'size': '35'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'rows': '7', 'cols': '60'}))

    # Zmieniamy pole recipient, aby odnosiło się do modelu Referee
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        to_field_name='id',
        label="Adresat",
        widget=forms.Select(attrs={'size': '5'}),  # Dodajemy atrybut size
        empty_label=None
    )
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']

class RefereeEditForm(forms.ModelForm):
    class Meta:
        model = Referee
        fields = ['name', 'surname', 'address', 'phone_number', 'date_of_birth']

class CustomUserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super(CustomUserEditForm, self).__init__(*args, **kwargs)
        del self.fields['password']

class CustomChangePasswordForm(forms.Form):
    old_password = forms.CharField(label="Stare hasło", widget=forms.PasswordInput)
    new_password1 = forms.CharField(label="Nowe hasło", widget=forms.PasswordInput)
    new_password2 = forms.CharField(label="Potwierdź nowe hasło", widget=forms.PasswordInput)

    field_order = ['old_password', 'new_password1', 'new_password2']

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()

        old_password = cleaned_data.get('old_password')
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        # Sprawdzanie starego hasła
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Niepoprawne stare hasło.')

        # Sprawdzanie spójności nowego hasła
        if new_password1 != new_password2:
            raise forms.ValidationError('Hasła nie są identyczne.')

        if len(new_password1) < 5:
            raise forms.ValidationError('Hasło musi mieć co najmniej 5 znaków.')

        return cleaned_data

class MatchForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.is_bound:
            class_match = self.data.get('class_match')
            if class_match:
                self.fields['referee'].queryset = Referee.objects.filter(class_referee=class_match)

    data_match = forms.DateField(label="Data", widget=forms.DateInput(attrs={"type": "date"}))
    time_match = forms.TimeField(label="Godzina meczu", widget=forms.TimeInput(attrs={"type": "time"}))
    class Meta:
        model = Match
        fields = [
            'team_a', 'team_b', 'class_match',
            'data_match', 'time_match',
             'referee', 'referee_assistant1', 'referee_assistant2'
        ]

