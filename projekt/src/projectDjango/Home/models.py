
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Referee(models.Model):
    CLASS_OF_REFEREE = (
        ('IV LIGA', 'IV LIGA'),
        ('Klasa Okręgowa', 'Klasa Okręgowa'),
        ('A Klasa', 'A Klasa'),
        ('B Klasa', 'B Klasa'),
        ('Pozostali', 'Pozostali'),

    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="referee")
    name = models.CharField(max_length=100, default='Nieznane')
    surname = models.CharField(max_length=100, default='Nieznane')
    address = models.CharField(max_length=100, default='Nieznany')
    phone_number = models.CharField(max_length=9, default='Nieznany')
    date_of_birth = models.DateField(default='2000-01-01')
    email = models.CharField(max_length=100, default='Nieznany')
    class_referee = models.CharField(max_length=100, choices=CLASS_OF_REFEREE, default='B Klasa')

    def __str__(self):
        return f"{self.name} {self.surname} - {self.user.username}"

class RefereeAvailability(models.Model):
    referee = models.ForeignKey(to=Referee, on_delete=models.CASCADE, related_name="availabilities")
    vacation = models.BooleanField(default=False)
    date = models.DateField()
    time_start = models.TimeField()
    time_finish = models.TimeField()
    number_of_matches = models.PositiveIntegerField()
    possible_distance_match = models.PositiveIntegerField(default=0)  # w kilometrach


class Team(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'


class Match(models.Model):
    CLASS_OF_MATCH = (
        ('IV LIGA', 'IV LIGA'),
        ('Klasa Okręgowa', 'Klasa Okręgowa'),
        ('A Klasa', 'A Klasa'),
        ('B Klasa', 'B Klasa'),

        # ... można dodać więcej klasyfikacji
    )

    class_match = models.CharField(max_length=50, choices=CLASS_OF_MATCH)
    team_a = models.ForeignKey(Team, related_name="team_home", on_delete=models.CASCADE)
    team_b = models.ForeignKey(Team, related_name="team_visit", on_delete=models.CASCADE)
    data_match = models.DateTimeField(null=True)
    time_match = models.TimeField(null=True)
    referee = models.ForeignKey(Referee, related_name="match_referee", on_delete=models.SET_NULL, null=True, blank=True)
    referee_assistant1 = models.ForeignKey(Referee, related_name="match_referee_assistant1", on_delete=models.SET_NULL, null=True, blank=True)
    referee_assistant2 = models.ForeignKey(Referee, related_name="match_referee_assistant2", on_delete=models.SET_NULL, null=True, blank=True)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    body = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    sender_deleted = models.BooleanField(default=False)
    recipient_deleted = models.BooleanField(default=False)

class Secretary(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Możliwe dodatkowe informacje specyficzne dla obsadzających

def validate_phone_number(value):
    if not value.isdigit():
        raise ValidationError('Nr telefonu powinien składać się tylko z cyfr.')
    if len(value) != 9:
        raise ValidationError('Nr telefonu powinien składać się z 9 cyfr.')

phone_number = models.CharField(max_length=9, validators=[validate_phone_number])
# Create your models here.
