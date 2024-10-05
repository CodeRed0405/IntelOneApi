from django.urls import path
from . import views



urlpatterns = [
    path('',views.index, name='index'),
    path('retrieve/', views.retrieve, name='retrieve'),
    path('view_applicant/', views.view_the_applicant, name='view_the_applicant'),
    path('show_all_applicants/', views.show_all_applicants, name='show_all_applicants'),
    path('dashboard/',views.dashboard, name='dashboard'),
    path('create_role/',views.create_role, name='create_role'),

]
