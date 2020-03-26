from django.urls import path

from apps.commodities import views

urlpatterns = [
    path('trade-partners/', views.TradePartnerList.as_view()),
    path('trade-partners/<int:pk>/', views.TradePartnerDetail.as_view()),
]
