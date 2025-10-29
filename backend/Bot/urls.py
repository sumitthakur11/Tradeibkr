"""
URL configuration for Bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Tradingbot import views

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/csrf_token',views.get_csrf_token,name= "token"),

    path('api/login',views.LoginAPI.as_view(),name='login'),
    path('api/broker', views.broker.as_view(), name="broker"),
    path('api/placeorder', views.placeorder.as_view(), name="placeholder"),
    path('api/symbols', views.Getsymbols.as_view(), name="symbol"),
    path('api/loginbroker', views.loginbroker.as_view(), name="loginbroker"),
    path('api/loginredirect', views.loginbrokerredirect.as_view(), name="loginbroker"),

    
    path('api/logoutbroker', views.logoutbroker.as_view(), name="logoutbroker"),
    path('api/position', views.postionsobj.as_view(), name="logoutbroker"),
    # path('api/watchlist', views.watchlist.as_view(), name="logoutbroker"),
    path('api/loadaccount', views.loadaccount.as_view(), name="logoutbroker"),
    path('api/sendlog', views.sendlog.as_view(), name="sendlog"),
    path('api/getfunds', views.getfunds.as_view(), name="getfunds"),
    path('api/getlogs', views.GetLogs.as_view(), name="getlogs"),
    path('api/getposition', views.getposition.as_view(), name="getposition"),
    path('api/getholding', views.getholding.as_view(), name="getholding"),
    path('api/v1/ibkr/orderdata', views.publicorderdata.as_view(), name="public-order-data"),
    path('api/v1/ibkr/positiondata', views.publicpositiondata.as_view(), name="public-position-data"),
    path('api/v1/ibkr/holdingsdata', views.publicholdingdata.as_view(), name="public-holdings-data"),
    path('api/v1/ibkr/getorderrequest', views.getpublicplaceorder.as_view(), name="public-get-order-request"),
    path('api/v1/ibkr/placeorder', views.getpublicplaceorder.as_view(), name="public-place-order"),
    path('api/v1/ibkr/forlogs', views.getforlogs.as_view(), name="getforlogs"),
    path('api/v1/ibkr/getfund', views.publicgetfunds.as_view(), name="getforlogs"),
    path ('api/v1/ibkr/downloadlog', views.DownloadLogsAPI.as_view(), name="downloadlog"),
    path ('api/orderrequest', views.orderrequest.as_view(), name="downloadlog"),
    path ('api/v1/ibkr/cancelreq', views.getpubliccancel.as_view(), name="getpubliccancel"),
    path ('api/v1/ibkr/modifyreq', views.getpublicmodify.as_view(), name="modifyreq"),
    path ('api/v1/ibkr/connection', views.getpubliconnection.as_view(), name="connections"),






    


    
    




]
