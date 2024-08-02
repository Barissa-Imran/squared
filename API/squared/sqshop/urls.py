from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, OrderItemViewSet, OrderViewSet, AddressViewSet, TransactionViewSet, CouponViewSet, RefundViewSet


router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'addresses', AddressViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'coupons', CouponViewSet)
router.register(r'refunds', RefundViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
