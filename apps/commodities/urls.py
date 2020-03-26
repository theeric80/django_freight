from django.urls import path, include

from rest_framework.routers import DefaultRouter

from apps.commodities import views

router = DefaultRouter()
router.register(r'inventories', views.InventoryViewSet)

urlpatterns = [
    path('trade-partners/', views.TradePartnerList.as_view()),
    path('trade-partners/<int:pk>/', views.TradePartnerDetail.as_view()),
    path('commodities/', views.CommodityList.as_view()),
    path('commodities/<int:pk>/', views.CommodityDetail.as_view()),
    path('', include(router.urls)),
]
