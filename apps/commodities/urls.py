from django.urls import path

from apps.commodities import views

urlpatterns = [
    path('trade-partners/', views.TradePartnerList.as_view()),
    path('trade-partners/<int:pk>/', views.TradePartnerDetail.as_view()),
    path('commodities/', views.CommodityList.as_view()),
    path('commodities/<int:pk>/', views.CommodityDetail.as_view()),
]
