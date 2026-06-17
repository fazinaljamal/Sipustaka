from django.urls import path
from . import views


urlpatterns = [
    
    path('',views.dashboard,name='dashboard'),
    path('buku/',views.buku_list, name='buku_list'),
    path('buku/<int:id>/',views.buku_detail, name='buku_detail'),
    path('buku/create/',views.buku_create, name='buku_create'),
    path('buku/update/<int:id>/',views.buku_update, name='buku_update'),
    path('buku/delete/<int:id>/',views.buku_delete, name='buku_delete'),
    path('peminjaman/',views.peminjaman_list, name='peminjaman_list'),
    path('peminjaman/create/',views.peminjaman_create, name='peminjaman_create'),
    path('peminjaman/kembalikan/<int:id>/', views.peminjaman_kembalikan, name='peminjaman_kembalikan'),
    path('user/',views.user_list, name='user_list'),
    path('user/<int:id>/',views.user_detail, name='user_detail'),
    path('user/create/',views.user_create, name='user_create'),
    path('user/update/<int:id>/',views.user_update, name='user_update'),
    path('user/delete/<int:id>/',views.user_delete, name='user_delete')


]