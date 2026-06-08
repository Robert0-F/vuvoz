from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    AdminAuditLogExportView,
    AdminDatabaseInfoView,
    AdminAuditLogListView,
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
    CompanyRegistrationRequestViewSet,
    InstitutionStatsView,
    InstitutionViewSet,
    MaterialViewSet,
    NewsArticleViewSet,
    NotificationViewSet,
    PointsOrderViewSet,
    PriceListViewSet,
    ProductCategoryViewSet,
    ProductViewSet,
    PublicMaterialsView,
    PublicProductCategoriesView,
    PublicProductsView,
    PublicPickupRequestViewSet,
    PublicWeightLimitsView,
    SupportAssignedInstitutionsView,
    SupportChatMarkReadView,
    SupportChatMessageView,
    SupportConfigView,
    SupportUserListCreateView,
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
router.register(r'product-categories', ProductCategoryViewSet, basename='productcategory')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'registration-requests', InstitutionRegistrationRequestViewSet, basename='registrationrequest')
router.register(r'company-registration-requests', CompanyRegistrationRequestViewSet, basename='company-registrationrequest')
router.register(r'public/pickup-requests', PublicPickupRequestViewSet, basename='public-pickup-request')
router.register(r'points-orders', PointsOrderViewSet, basename='pointsorder')

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('public/materials/', PublicMaterialsView.as_view(), name='public-materials'),
    path('public/products/', PublicProductsView.as_view(), name='public-products'),
    path('public/products/categories/', PublicProductCategoriesView.as_view(), name='public-product-categories'),
    path('public/weight-limits/', PublicWeightLimitsView.as_view(), name='public-weight-limits'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('stats/company/', CompanyStatsView.as_view(), name='stats-company'),
    path('stats/company/dashboard/', CompanyDashboardView.as_view(), name='stats-company-dashboard'),
    path('stats/institution/', InstitutionStatsView.as_view(), name='stats-institution'),
    path('stats/admin/', AdminStatsView.as_view(), name='stats-admin'),
    path('analytics/dashboard/', AdminAnalyticsView.as_view(), name='analytics-dashboard'),
    path('audit-logs/', AdminAuditLogListView.as_view(), name='audit-logs'),
    path('audit-logs/export/', AdminAuditLogExportView.as_view(), name='audit-logs-export'),
    path('database-info/', AdminDatabaseInfoView.as_view(), name='database-info'),
    path('me/points/', InstitutionPointsView.as_view(), name='institution-points'),
    path('weight-limits/', WeightLimitsView.as_view(), name='weight-limits'),
    path('bonus-config/', BonusConfigView.as_view(), name='bonus-config'),
    path('support-config/', SupportConfigView.as_view(), name='support-config'),
    path('support-users/', SupportUserListCreateView.as_view(), name='support-users'),
    path('support/institutions/', SupportAssignedInstitutionsView.as_view(), name='support-institutions'),
    path('support/chats/<int:institution_id>/', SupportChatMessageView.as_view(), name='support-chat-messages'),
    path('support/chats/<int:institution_id>/read/', SupportChatMarkReadView.as_view(), name='support-chat-read'),
    path('institution-bonuses/', InstitutionBonusViewSet.as_view({'get': 'list'})),
    path('institution-bonuses/<int:pk>/', InstitutionBonusViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'put': 'partial_update'})),
    path('', include(router.urls)),
    path('me/', CurrentUserView.as_view(), name='current-user'),
]
