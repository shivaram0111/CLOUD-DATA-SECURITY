from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"), #
    path('login/', views.login, name="login"), #
    path('user/', views.user, name="user"), #
    path('viewusers/', views.viewusers, name="viewusers"), #
    path('acceptuser/<int:id>', views.acceptuser, name='acceptuser'), #
    path('viewcloudfiles/', views.viewcloudfiles, name='viewcloudfiles'), #
    path('viewfilesrequest/', views.viewfilesrequest, name='viewfilesrequest'), #
    path('acceptfilerequest/<int:id>', views.acceptfilerequest, name='acceptfilerequest'), #
    path('encryptdata/', views.encryptdata, name='encryptdata'), #
    path('viewfiles/', views.viewfiles, name='viewfiles'), #
    path('sendrequest/<int:id>', views.sendrequest, name="sendrequest"), #
    path('filerequest/', views.filerequest, name='filerequest'), #
    path('sendkey/<int:fileid>', views.sendkey, name='sendkey'), #
    path('decryptdata/', views.decryptdata, name='decryptdata'), #
    path('viewmyfiles/<int:id>', views.viewmyfiles, name="viewmyfiles"), #
    path('logout/', views.logout_view, name='logout'), #
    path('filetransactions/', views.filetransactions, name='filetransactions'), #
    path('download/<int:file_id>/', views.download_encrypted_file, name='download_encrypted_file'), #
    path('userhome/', views.userhome, name='userhome'), #
]