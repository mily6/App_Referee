from . import views
from .views import MessagesView, delete_message
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import delete_match

urlpatterns = [
    path('register_referee/', views.register_referee, name='register_referee'),
    path('login/', views.login_view, name='login'),  # załóżmy, że funkcja widoku nazywa się 'login_view'
    path('', views.logged_view, name='logged'),  # załóżmy, że funkcja widoku nazywa się 'login_view'
    path('preferences/', views.PreferencesView.as_view(), name='preferences'),
    path('editReferee/', views.editReferee, name='editReferee'),
    path('editPassword/', views.editPassword, name='editPassword'),
    path('castCaster/', views.castCasterView.as_view(), name='castCaster'),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='reset_password'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('delete_match/<int:match_id>/', delete_match, name='delete_match'),
    path('get_match_data/<int:match_id>/', views.get_match_data, name='get_match_data'),
    path('edit_match/<int:match_id>/', views.edit_match, name='edit_match'),
    path('get_referees_by_class/', views.get_referees_by_class, name='get_referees_by_class'),

]

# messages
urlpatterns += [
    path('messages/', views.MessagesView.as_view(), name='messages'),
    path('messages/delete/<int:message_id>/', delete_message, name='delete_message'),  # dodaj to
    path('messages/all/', views.MessageToAll.as_view(), name='message-all')
]