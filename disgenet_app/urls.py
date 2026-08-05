from django.urls import path
from . import views

app_name = 'disgenet_app'

urlpatterns = [
    path('', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('stats/', views.stats, name='stats'),

    path('api/scores/', views.api_scores_distribution, name='api_scores'),
    path('api/gda-by-year/', views.api_gda_by_year, name='api_gda_year'),
    path('api/disease-types/', views.api_disease_types_pie, name='api_disease_types'),

    path('api/vda-scores/', views.api_vda_scores_distribution, name='api_vda_scores'),
    path('api/vda-by-year/', views.api_vda_by_year, name='api_vda_year'),

    path('disease/<str:disease_id>/', views.disease_detail, name='disease_detail'),
]