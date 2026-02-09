from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    CollectionRequestViewSet,
    CompanyProfileViewSet,
    CompanyStatsView,
    CurrentUserView,
    InstitutionStatsView,
    InstitutionViewSet,
    NewsArticleViewSet,
    NotificationViewSet,
    PriceListViewSet,
)

router = DefaultRouter()
router.register(r'company-profiles', CompanyProfileViewSet, basename='companyprofile')
router.register(r'institutions', InstitutionViewSet, basename='institution')
router.register(r'collection-requests', CollectionRequestViewSet, basename='collectionrequest')
router.register(r'news', NewsArticleViewSet, basename='news')
router.register(r'prices', PriceListViewSet, basename='pricelist')
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('stats/company/', CompanyStatsView.as_view(), name='stats-company'),
    path('stats/institution/', InstitutionStatsView.as_view(), name='stats-institution'),
    path('', include(router.urls)),
    path('me/', CurrentUserView.as_view(), name='current-user'),
]
