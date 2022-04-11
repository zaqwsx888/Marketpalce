from django.urls import path
from .views import PaymentsAPIView

urlpatterns = [
    path('pay/', PaymentsAPIView.as_view(), name='payments_api')
]
