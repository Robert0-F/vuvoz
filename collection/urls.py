from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AdminAnalyticsView,
    AdminStatsView,
    BonusConfigView,
    CollectionRequestViewSet,
    CompanyProfileViewSet,
    CompanyStatsView,
    CompanyDashboardView,
    CurrentUserView,
    HealthView,
    InstitutionBonusViewSet,
    InstitutionPointsView,
    InstitutionRegistrationRequestViewSet,
    InstitutionStatsView,
    InstitutionViewSet,
    MaterialViewSet,
    NewsArticleViewSet,
    NotificationViewSet,
    PointsOrderViewSet,
    PriceListViewSet,
    ProductViewSet,
    WeightLimitsView,
)

router = DefaultRouter()
router.register(r'company-profiles', CompanyProfileViewSet, basename='companyprofile')
router.register(r'institutions', InstitutionViewSet, basename='institution')
router.register(r'collection-requests', CollectionRequestViewSet, basename='collectionrequest')
router.register(r'news', NewsArticleViewSet, basename='news')
router.register(r'materials', MaterialViewSet, basename='material')
router.register(r'prices', PriceListViewSet, basename='pricelist')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'registration-requests', InstitutionRegistrationRequestViewSet, basename='registrationrequest')
router.register(r'points-orders', PointsOrderViewSet, basename='pointsorder')

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('stats/company/', CompanyStatsView.as_view(), name='stats-company'),
    path('stats/company/dashboard/', CompanyDashboardView.as_view(), name='stats-company-dashboard'),
    path('stats/institution/', InstitutionStatsView.as_view(), name='stats-institution'),
    path('stats/admin/', AdminStatsView.as_view(), name='stats-admin'),
    path('analytics/dashboard/', AdminAnalyticsView.as_view(), name='analytics-dashboard'),
    path('me/points/', InstitutionPointsView.as_view(), name='institution-points'),
    path('weight-limits/', WeightLimitsView.as_view(), name='weight-limits'),
    path('bonus-config/', BonusConfigView.as_view(), name='bonus-config'),
    path('institution-bonuses/', InstitutionBonusViewSet.as_view({'get': 'list'})),
    path('institution-bonuses/<int:pk>/', InstitutionBonusViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'partial_update'})),
    path('', include(router.urls)),
    path('me/', CurrentUserView.as_view(), name='current-user'),
]
