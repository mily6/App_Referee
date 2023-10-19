from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from .models import Referee, RefereeAvailability
from .forms import RefereeAvailabilityForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.views.generic import CreateView
from datetime import date
from .models import Message, Match
from .forms import MessageForm
from django.core.paginator import Paginator
from .forms import RefereeEditForm, CustomUserEditForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from .forms import CustomChangePasswordForm
from collections import OrderedDict
from django.contrib.auth.decorators import login_required
from django.views import View
from .forms import MatchForm
from django.http import JsonResponse

def register_referee(request):
    if request.method == 'POST':
        # Wyodrębnij dane z request.POST
        fields = {
            'username': request.POST.get('username'),
            'password1': request.POST.get('password1'),
            'password2': request.POST.get('password2'),
            'email': request.POST.get('email'),
            'name': request.POST.get('name'),
            'surname': request.POST.get('surname'),
            'address': request.POST.get('address'),
            'phone_number': request.POST.get('phone_number'),
            'date_of_birth': request.POST.get('date_of_birth')
        }

        for field, value in fields.items():
            if not value:  # Jeśli pole jest puste
                error_message = f"Pole {field} jest wymagane."
                return render(request, 'registration/register.html', {'error_message': error_message})

        if fields['password1'] != fields['password2']:
            error_message = "Hasła nie są takie same."
            return render(request, 'registration/register.html', {'error_message': error_message})

        # Teraz możesz dodać własną logikę walidacji tych danych (na przykład sprawdzanie, czy hasła się zgadzają itp.)
        # ...

        # Jeśli wszystko jest w porządku, zapisz użytkownika
        user = User.objects.create_user(username=fields['username'], password=fields['password1'], email=fields['email'])
        referee = Referee(
            user=user,
            name=fields['name'],
            surname=fields['surname'],
            address=fields['address'],
            phone_number=fields['phone_number'],
            date_of_birth=fields['date_of_birth'],
        )

        try:
            referee.full_clean()  # Przeprowadź walidację danych modelu
        except ValidationError as e:
            return render(request, 'registration/register.html', {'error_message': str(e)})

        referee.save()
        return redirect('login')

    # Jeśli to nie POST, po prostu renderuj stronę z formularzem
    return render(request, 'registration/register.html')


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('logged')  # na przykład: 'home'
        else:
            messages.error(request, 'Błędna nazwa użytkownika lub hasło')
            return render(request, 'login/login.html', {'form': form})
    else:
        form = AuthenticationForm()
        return render(request, 'login/login.html', {'form': form})

def logged_view(request):
    try:
        referee = Referee.objects.get(user=request.user)
    except Referee.DoesNotExist:
        referee = None
    return render(request, 'logged/logged2.html', {'referee': referee})

# def preferences_view(request):
#     try:
#         referee = Referee.objects.get(user=request.user)
#     except Referee.DoesNotExist:
#         referee = None
#
#         # Przekazanie sędziego do kontekstu szablonu
#     context = {'referee': referee}
#     return render(request, 'preferences/preferences.html', context)


class PreferencesView(LoginRequiredMixin, CreateView):
    template_name = 'preferences/preferences2.html'
    form_class = RefereeAvailabilityForm
    success_url = "preferences/preferences2.html"

    def form_valid(self, form):
        print("Form is valid!")  # Dodaj tę linię
        form.instance.referee = Referee.objects.get(user=self.request.user)
        if form.instance.vacation:
            form.instance.time_start = None
            form.instance.time_finish = None
            form.instance.possible_distance_match = 0
            form.instance.number_of_matches = 0
        self.object = form.save()
        return redirect('preferences')  # przekierowuje do samego siebie, można dostosować

    def form_invalid(self, form):
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            referee = Referee.objects.get(user=self.request.user)
        except Referee.DoesNotExist:
            referee = None

        context['availabilities'] = RefereeAvailability.objects.filter(referee=referee, date__gt=date.today())
        context['referee'] = referee

        return context


        '''return super().form_valid(form)'''


class MessagesView(LoginRequiredMixin, CreateView):
    template_name = 'messages/messages2.html'
    form_class = MessageForm
    success_url = "messages/messages2.html"

    def form_valid(self, form):
        form.instance.sender = self.request.user
        self.object = form.save()
        return redirect('messages')

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(MessagesView, self).get_context_data(**kwargs)
        if len(Referee.objects.filter(user=self.request.user)) > 0:
            context['referee'] = Referee.objects.get(user=self.request.user)

        inbox_messages = Message.objects.filter(recipient=self.request.user, recipient_deleted=False).order_by('-date_sent')
        paginator = Paginator(inbox_messages, 10)  # 10 wiadomości na stronę
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['inbox_messages'] = page_obj.object_list
        context['page_obj'] = page_obj  # przekazujemy obiekt strony do kontekstu
        # Dodanie wiadomości do kontekstu
        context['sent_messages'] = Message.objects.filter(sender=self.request.user).order_by('-date_sent')

        sent_messages = Message.objects.filter(sender=self.request.user, sender_deleted=False).order_by('-date_sent')
        sent_paginator = Paginator(sent_messages, 10)  # 10 wiadomości na stronę
        sent_page_number = self.request.GET.get('sent_page')
        sent_page_obj = sent_paginator.get_page(sent_page_number)
        context['sent_messages'] = sent_page_obj.object_list
        context['sent_page_obj'] = sent_page_obj  # przekazujemy obiekt strony do kontekstu

        return context

    def mailbox(request):
        if request.method == "POST":
            form = MessageForm(request.POST)
            if form.is_valid():
                message = form.save(commit=False)
                message.sender = request.user
                message.save()
                return redirect('messages')

        else:
            form = MessageForm()

        # Tutaj również pobierasz wiadomości, więc możesz użyć tego samego fragmentu
        inbox_messages = Message.objects.filter(recipient=request.user).order_by('-date_sent')
        return render(request, 'messages.html', {'form': form, 'inbox_messages': inbox_messages})


def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    # Sprawdź, czy żądający jest nadawcą czy odbiorcą
    if request.user == message.sender:
        message.sender_deleted = True
    elif request.user == message.recipient:
        message.recipient_deleted = True

    # Sprawdzenie, czy obie strony usunęły wiadomość
    if message.sender_deleted and message.recipient_deleted:
        message.delete()
    else:
        message.save()

    return redirect('messages')

def editReferee(request):
    referee = Referee.objects.get(user=request.user)
    user = request.user

    if request.method == 'POST':
        form = RefereeEditForm(request.POST, instance=referee)
        user_form = CustomUserEditForm(request.POST, instance=user)

        if form.is_valid() and user_form.is_valid():
            form.save()
            user_form.save()
            messages.success(request, "Dane zostały zaaktualizowane")
            return redirect('editReferee')

    else:
        form = RefereeEditForm(instance=referee)
        user_form = CustomUserEditForm(instance=user)

    return render(request, 'editReferee/editReferee2.html', {'form': form, 'user_form': user_form})

@login_required
def editPassword(request):
    if request.method == "POST":
        form = CustomChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()
            messages.success(request, 'Hasło zostało zmienione!')
            return redirect('login') # Dostosuj
        else:
            # Tu możesz obsłużyć błędy, na przykład wyświetlić je użytkownikowi
            pass
    else:
        form = CustomChangePasswordForm(request.user)
    return render(request, 'editPassword/editPassword2.html', {'form': form})


class MessageToAll(View):
    def post(self, request):
        subject = request.POST['subject']
        body = request.POST['body']
        recipients = User.objects.all()
        sender = request.user

        for r in recipients:
            if r != sender:
                Message.objects.create(sender=sender, recipient=r, subject=subject, body=body)

        return redirect('messages')

class castCasterView(LoginRequiredMixin, CreateView):
    template_name = 'castCaster/castCaster.html'
    form_class = MatchForm
    success_url = 'castCaster/castCaster.html'

    def form_valid(self, form):
        self.object = form.save()
        return redirect('castCaster')  # dostosuj do właściwej ścieżki URL

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            referee = Referee.objects.get(user=self.request.user)
        except Referee.DoesNotExist:
            referee = None

        context['referee'] = referee
        context['matches'] = Match.objects.all() # Możesz dodać więcej kontekstu jeśli to konieczne
        return context

def delete_match(request, match_id):
    if request.method == "POST":
        Match.objects.filter(pk=match_id).delete()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False, "error": "Invalid method."})

def get_match_data(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    data = {
        'team_a_id': match.team_a.id,
        'team_b_id': match.team_b.id,
        'class_match': match.class_match,
        'data_match': match.data_match.strftime('%Y-%m-%d'),
        'time_match': match.time_match.strftime('%H:%M'),
        'referee_id': match.referee.id if match.referee else None,
        'referee_assistant1_id': match.referee_assistant1.id if match.referee_assistant1 else None,
        'referee_assistant2_id': match.referee_assistant2.id if match.referee_assistant2 else None,
    }
    return JsonResponse(data)

def edit_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)

    if request.method == "POST":
        form = MatchForm(request.POST, instance=match)  # używamy instance, aby edytować istniejący obiekt

        if form.is_valid():
            form.save()
            # Przekierowuj do odpowiedniej strony po zapisaniu
            return redirect('castCaster')
    else:
        MatchForm(instance=match)

    # Możesz tu również przekazać formularz do szablonu, jeśli potrzebujesz
    # return render(request, 'nazwa_twojego_szablonu.html', {'form': form})

def get_referees_by_class(request):
    class_match = request.GET.get('class_match')
    match_date = request.GET.get('match_date')  # format 'YYYY-MM-DD'
    match_time = request.GET.get('match_time')  # format 'HH:MM'

    referees = Referee.objects.filter(referee_class=class_match)

    # Filtruj sędziów na podstawie dostępności
    # for referee in referees:
    #     availability = referee.availabilities.filter(date=match_date).first()
    #     if availability:
    #         if not (availability.time_start <= match_time <= availability.time_finish):
    #             referees = referees.exclude(id=referee.id)

    referee_options = [{'id': referee.id, 'name': str(referee)} for referee in referees]
    return JsonResponse({'referee_options': referee_options})