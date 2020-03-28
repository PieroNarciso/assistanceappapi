from django.urls import include, path

from rest_framework import routers

from . import views


router = routers.DefaultRouter()
router.register('assistances', views.AssistanceViewSet)
router.register('users', views.UserViewSet)
router.register('codes', views.NumCodeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.CustomAuthToken.as_view()),
    path('auth/get-code/', views.NumCodeLastView.as_view()),
    path('auth/get-user/', views.GetUserView.as_view())
]
