from django.shortcuts import render
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework import generics,permissions,status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.generics import GenericAPIView,UpdateAPIView
from rest_framework.decorators import api_view

from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import get_token


from . import serializers as ser 
from . import models as md
import datetime
from . import env
import os
import pathlib
path = pathlib.Path(__file__).resolve().parent.parent
logpath= os.path.join(path,'Botlogs/Frontendlog.logs')
logpath= os.path.normpath(logpath)
import json
import pytz
import time
from .utility import get_tokens_for_user,verify_token
# optional third-party SDK - if not installed, fall back to None and handle gracefully
from .utility import IBKR
from django.http import JsonResponse, FileResponse, Http404
import locale
from rest_framework.exceptions import ValidationError as DRFValidationError
import traceback
# from .utility import utility

print(logpath,'logpath')
logger=env.setup_logger(logpath)

# Create your views here.
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})








class LoginAPI(KnoxLoginView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    # @csrf_exempt
    def post(self, request, format=None):
            try:
                serializer = AuthTokenSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = serializer.validated_data['user']
            
                login(request, user)
                
                user_login = super(LoginAPI, self).post(request, format=None)
                format= '%Y-%m-%dT%H:%M:%S.%f%z'
                user_login.data['expiry']= datetime.datetime.strptime(user_login.data['expiry'],format).timestamp()
                print(user_login.data)
                logger.info("Login Sucessfull")

                return Response({"message":user_login.data,
                                "id":user.id},
                                status=status.HTTP_200_OK)
                
            except DRFValidationError as e:
                # DRF ValidationError -> return its serializable .detail
                logger.warning(f'Validation error during login: {e}')
                return Response({
                            "message": e.detail,
                            "code": status.HTTP_400_BAD_REQUEST
                        },  
                        status=status.HTTP_400_BAD_REQUEST)
            except Exception as e :
                # Ensure exception is converted to a serializable form (string)
                logger.error(traceback.format_exc())
                return Response({
                            "message": str(e),
                            "code": status.HTTP_400_BAD_REQUEST
                        },  
                        status=status.HTTP_400_BAD_REQUEST)


class broker(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            users = request.user
            proj= md.Broker.objects.filter(user=users.id,brokername='IBKR',status=True).values('status','brokerid','nickname','accountnumber','access_token','refresh_token','funds')
            print(proj)
            
            return Response({"message":proj})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


    # @csrf_exempt
    def post(self, request):
        user = request.user
        data=dict()
        try:
            if not request.data.get('brokerid'):

                print(request.data)
                request.data['brokername']=request.data.get('brokerName')
                request.data['user']= user.id
                tokens = get_tokens_for_user(request.user, accountnumber=request.data.get('accountnumber'))
                request.data['access_token']= tokens['access']
                request.data['refresh_token']= tokens['refresh']

                serialize = ser.Broker(data=request.data)

                if serialize.is_valid(raise_exception=True):
                        serialize.save()
                
            
                logger.info('Broker added sucessfully')
                
                return Response({"Message":'sucessfl'},status=status.HTTP_200_OK)


          
           
           

            
        except Exception as e:
            logger.error(e)
            
            return Response({
                    "Message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        

    def put(self, request, *args, **kwargs):
        """
        Update the profile
        user.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        try:

            user = request.user
            print(request.data)
            put=request.data.get('put')
            if not put :
                proj= md.Broker.objects.filter(brokerid=request.data.get('brokerid')).last()
                proj.active= False if proj.active else True
                print(proj.brokername)
                if proj.brokername=='GROWW':    
                    proj.valid=True
                if proj.brokername=='DHAN':    
                    proj.valid=True

                proj.save()

            else :
                    serialize = ser.Broker(data=request.data)
                    serialize.is_valid(raise_exception=True)
                    valuessetbr = serialize.validated_data
                    md.Broker.objects.filter(brokerid=request.data.get('brokerid')).update(**valuessetbr)
                    print(put)

            logger.info('Broked saved')

                

                
            
        
            return Response(
                {"Message": "Successfully Updated Attendance"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,*args,**kwargs):
        try:

            user = request.user
              
            print(request.GET.get('brokerid'))
            if int(request.GET.get('brokerid')) == 0:

                block= md.Broker.objects.filter(user=user.id,brokerid=request.GET.get('brokerid'))
                for i in block:
                 

                    i.delete()
            else:
              block=  md.Broker.objects.filter(user=user.id,brokerid=request.GET.get('brokerid')).last()
              block.delete()    

            return Response({"message":'deleted'})
            
        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


brokerlist=[
    {"NAME":"IBKR"},
  



    
]

import requests
import pandas as pd
import io


def get_symbol_info(symbol, exchange, ETF='N'):
            

            url ='https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt' if  exchange in ['N','A','V','M']  else 'https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt'
            symbolinfolist=requests.get(url).text

            symbolinfolist= pd.read_csv(io.StringIO(symbolinfolist),delimiter='|')
            print(symbolinfolist.head())
            print(symbolinfolist.columns)   
            if exchange in ['N','A','V','M']:
                symbolinfolist= symbolinfolist.rename(columns={'ACT Symbol':'Symbol','Security Name':'Name','Exchange':'Exchange','ETF':'ETF','Lot Size':'LotSize','Test Issue':'TestIssue','NASDAQ Symbol':'NASDAQSymbol'})
            else:
                symbolinfolist= symbolinfolist.rename(columns={'Symbol':'Symbol','Security Name':'Name','Market Category':'Instrument','ETF':'ETF','Round Lot Size':'LotSize','Test Issue':'TestIssue'})
                symbolinfolist['Exchange']=exchange
                symbolinfolist['NASDAQSymbol']=symbolinfolist['Symbol']
                print('smiles')

            symbolinfolist=symbolinfolist[symbolinfolist['Symbol'] != '']
            symbolinfolist=symbolinfolist.dropna(subset=[ 'ETF'])
            print(symbolinfolist['ETF'].unique(),'ETF')
            print(symbolinfolist['Exchange'].unique(),'instruments')


            

            symbolinfolist['Symbol'] = symbolinfolist['Symbol'].str.strip()
            symbolinfolist = symbolinfolist.drop_duplicates(subset=['Symbol'], keep='first')
            symbolinfolist=symbolinfolist.reset_index(drop=True)
            symbbolinfo= symbolinfolist[(symbolinfolist['Exchange']== exchange) & (symbolinfolist['ETF']== ETF)]
            print(symbbolinfo,'symbbolinfo')
            print(symbolinfolist['Symbol'].unique(),'symbbolinfo')
            print(symbol,'symbollllllllllllllllllllllllllllllllllllllllll')
            symbbolinfo= symbbolinfo[symbbolinfo['Symbol'].str.contains(symbol, case=False, na=False)]
            if symbbolinfo.empty:

                symbbolinfo= symbbolinfo[symbbolinfo['NASDAQSymbol'].str.contains(symbol, case=False, na=False)]

            if symbbolinfo.empty:
                symbbolinfo= symbbolinfo[symbbolinfo['Name'].str.contains(symbol, case=False, na=False)]

                


            return symbbolinfo


class Getsymbols(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):


        try:
            print(request.GET,'request.GET')
            users = request.user
            
            data = []
            data1 = dict()
            exchange = (request.GET.get('exchange') or '').upper()
            instrument = (request.GET.get('instrument') or '').upper()
            name = (request.GET.get('name') or '')
            print(name,exchange)
            datas = get_symbol_info(name,exchange)
            print(datas,'datatatatatatatatata')

           
           

            
            return Response({"message": datas}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)

import json
class placeorder (GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):


        try:
            users = request.user
            # dash=utility(users)
            oderids= request.GET.get('selectedRows')
            print(type(oderids),oderids)
            data = json.loads(oderids)
            print(data[0]['id'])
            for i in data:
                data1= dict()
                data1['user']=users.id
                data1['cancel_order']=True
                data1['accountnumber']= i['accountnumber']
                data1['orderid']= i['orderid']
                holding = md.ordercancel.objects.create(**data1)
                data1={}

                 

            # dash.cancel_order(oderids)

            
           



            return Response({"message":'ok'},status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({
                    "message": e,
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)






    def post(self, request):
        user = request.user
        try:
            print("Incoming Data:", request.data)
            if not request.data.get("modify"):

                for i in request.data.get("accountname"):
                    
                    
                    data = {
                        "user": user.id,
                        "broker": request.data.get("brokerName4"),
                        "exchange": request.data.get("exchange"),
                        "instrument": 'EQ',
                        "tradingsymbol": request.data.get("selectsymbol"),
                        "ltp": request.data.get("price"),
                        "avg_price": request.data.get("price"),
                        'TIF':request.data.get('instrument'),
                        "symboltoken": request.data.get("token"),
                        "quantity": request.data.get("quantity"),
                        "ordertype":'LIMIT',
                        "product_type": request.data.get("product"),
                        "transactiontype": request.data.get("side"),
                        "accountnumber": i,  # store as JSON string if it's a list
                        "discloseqty": request.data.get("discloseqty"),
                        "lotsize": request.data.get("lotsize"),
                        "orderstatus": "PENDING",
                        'OUTSIDERTH':request.data.get("Rth")
                    }

                
                    allowed_fields = [f.name for f in md.orderobject._meta.get_fields()]
                    filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

                    order = md.orderobject.objects.create(**filtered_data)


            
            elif request.data.get("modify") and request.data.get("orderid"):
                request.data['user']= user.id
                request.data['modify_order']= True
                request.data['ordertype']= request.data.get('orderType')
                request.data['avg_price']= request.data.get('price')
                request.data['symboltoken']= request.data.get('token')
                request.data['symboltoken']= request.data.get('token')
                request.data['accountnumber']= request.data.get('accountname')

                






                serdata = ser.ordermodify(data=request.data)
                if serdata.is_valid(raise_exception=True):
                        serdata.save()


            return Response(
                {
                    "message": "Order saved successfully",
                   
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(traceback.format_exc())
            print(e)
            return Response(
                {"Message": str(e), "code": status.HTTP_400_BAD_REQUEST},
                status=status.HTTP_400_BAD_REQUEST,
            )


class loginbroker (GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        user = request.user
        data=dict()
        try:

       
        
            data['brokerid'] = request.data.get("brokerid")


            print(user.id)
            # dash=utility(user)
            # oid=dash.loginbroker(data)

          
           
           

            
            return Response({"message":"successful" },status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({
                    "Message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class loginbrokerredirect (GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):


        try:
            user = request.user

            data= dict()
            data['brokerid'] = request.GET.get("brokerid")
            # dash=utility(user)
            # oid=dash.loginbroker(data)
            time.sleep(2)
            db = md.Broker.objects.filter(brokerid=data['brokerid']).last()
            print(db.url,'urlssssssssssssssssssssssssssssssssssssssssssssss')
           



            return Response({"message":db.url},status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)




    def post(self, request):
        user = request.user
        data=dict()
        try:

       
        
            data['brokerid'] = request.data.get("brokerid")
            print(request.data)
            db = md.Broker.objects.filter(brokerid=int(data['brokerid'])).last()
            db.AuthToken=  request.data.get("accesstoken")
            db.save()


          
           
           

            
            return Response({"message":'ok' },status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e)
            return Response({
                    "Message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )




class logoutbroker (GenericAPIView):
    def post(self, request):
        user = request.user
        data=dict()
        try:


            # dash=utility(user)
            data['broker'] = request.data.get("brokerName3")
            # oid=dash.logoutbroker(data)
            return Response({"message":"successful" },status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({
                    "Message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    def get(self, request, *args, **kwargs):


        try:
            user = request.user

            data= dict()
            data['broker'] = request.GET.get("brokerName3")
            # dash=utility(user)
            # oid=dash.logoutbroker(data)

            return Response({"message":"successful" },status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST
                )


class postionsobj(GenericAPIView):
    # Token auth disabled to allow unauthenticated POSTs
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        try:
            finaldata= []
            users = request.user
            data = dict()
            start= datetime.datetime.now(tz= pytz.timezone('Asia/Kolkata')).replace(hour=23, minute=59, second=0, microsecond=0)
            end = start- datetime.timedelta(days=1)
            print(end,start)
            # dash=utility(users)
            
            # dash.orderstatus()

            if  request.GET.get('type')== "all":
                data = list(md.orderstatus.objects.filter(user=users.id,updated_at__range=(end,start)) .order_by('-lastmodifiedtime').values('accountnumber','tradingsymbol','transactiontype','orderstatus','quantity','filledqty','price','remarks','avg_price',
                                                                      'exchange','side','orderid','lastmodifiedtime','id','symboltoken'))

                
                

            return Response({"message":data})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)
    def post(self, request):
        try:
            user = request.user
           
            if not user or getattr(user, 'is_anonymous', True):
                return Response({"message": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

            incoming = request.data
            print("incommingssssssssssssssss", incoming)

            
            allowed = [f.name for f in md.orderobject._meta.get_fields()]
            filtered = {k: v for k, v in incoming.items() if k in allowed}
            filtered['user'] = user.id

            order = md.orderobject.objects.create(**filtered)

        
            return Response({"message": "ok", "order_id": order.id}, status=status.HTTP_200_OK)
        except Exception as e:
            print("##########", e)
            return Response({
                    "message": str(e),
                    "code": status.HTTP_400_BAD_REQUEST
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def put(self, request):
        try:
            user = request.user
            incoming = request.data
            order_id = incoming.get("id")
    
            if not order_id:
                return Response({"message": "Order ID required"}, status=status.HTTP_400_BAD_REQUEST)
    
            # filter by the IntegerField 'user' using the numeric id
            order = md.orderobject.objects.filter(id=order_id, user=user.id).first()
            if not order:
                return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
    
            # Update fields
            for key, value in incoming.items():
                # Never allow changing primary id or the user foreign/int field from request body
                if key in ('id', 'user'):
                    continue
                if hasattr(order, key):
                    setattr(order, key, value)
            order.save()
    
            return Response({"message": "Order updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class loadaccount(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):


        try:
            users = request.user
            data= []
            print(request.GET.get('broker'))
            data1= dict()

            broker_raw = request.GET.get('broker')
            broker_lc = (broker_raw or '').lower()
            broker_up = (broker_raw or '').upper()

           
            datas = []

            if broker_lc == 'all':
                datas = brokerlist
            else:
                datas = md.Broker.objects.filter(user=users.id,brokername='IBKR').values('status','brokerid','funds','nickname','accountnumber','access_token','updated_at','active')
           
            # datas is always defined (possibly empty) at this point
            return Response({"message": datas})

        except Exception as e:
            print(e)
            logger.error(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


class sendlog(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):


        try:
            users = request.user
            data= []
            
            with open (logpath) as file:
                # data= json.load(file)
                data=file.readlines()[-1000:]

                file.close
                # data.reverse()

            


            return Response({"message":data})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)
def format_in_indian_style(amount):
    s = str(amount)
    if '.' in s:
        before, after = s.split('.')
    else:
        before, after = s, None

    last3 = before[-3:]
    rest = before[:-3]
    if rest:
        rest = ",".join([rest[max(i - 2, 0):i] for i in range(len(rest), 0, -2)][::-1])
        formatted = rest + "," + last3
    else:
        formatted = last3

    if after:
        formatted += '.' + after

    return formatted


class getfunds(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            data = dict()
            
            datalist = md.Broker.objects.filter(user=user.id,valid= True).values('brokername','nickname','accountnumber','funds')
            # print(data)
            # ensure we return a list of dicts even if query returns empty
            if  request.GET.get('type')== "all":
                data = list(datalist)

            return Response({"message":data})
            
           



            

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        try:
            user = request.user
            # require authentication
            if not user or getattr(user, 'is_anonymous', True):
                return Response({"message": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

            incoming = request.data
            print("Incomingssss fundssssss", incoming)

            brokername = incoming.get("brokername")
            funds_value = incoming.get("funds", "0.00")

            # try to find existing broker for this user
            broker_obj = md.Broker.objects.filter(user=user.id, brokername=brokername).last()

            # if not found, create a new broker record so funds can be stored
            if not broker_obj:
                broker_obj = md.Broker.objects.create(
                    user=user.id,
                    brokername=brokername,
                    nickname=incoming.get("nickname") or None,
                    accountnumber=incoming.get("accountnumber") or None,
                    funds=funds_value,
                    valid=True,
                )
                return Response({"message": "Broker created and funds set", "brokerid": broker_obj.brokerid}, status=status.HTTP_201_CREATED)

            # update existing broker's funds
            broker_obj.funds = funds_value
            broker_obj.save()

            return Response({"message": "Funds updated successfully", "brokerid": broker_obj.brokerid}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def put(self, request):
        try:
            user = request.user
            incoming = request.data
            broker_id = incoming.get("brokerid")

            if not broker_id:
                return Response({"message": "brokerid required"}, status=status.HTTP_400_BAD_REQUEST)

            broker = md.Broker.objects.filter(user=user.id, brokerid=broker_id).first()
            if not broker:
                return Response({"message": "Broker not found"}, status=status.HTTP_404_NOT_FOUND)

            for key, value in incoming.items():
                if hasattr(broker, key):
                    setattr(broker, key, value)
            broker.save()

            return Response({"message": "Broker record updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class getposition(GenericAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            data = dict()

            # dash=utility(user)

            # oid=dash.getposition()
            datalist = md.Allpositions.objects.filter(user=user.id).values('nickname','tradingsymbol','netqty','buyavgprice','sellavgprice','ltp','broker','realised','unrealised','updated_at')
            

            return Response({"message":datalist})



        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)
            
    def post(self, request):
        try:
            user = request.user
            data = request.data
            data['user'] = user.id 
            
            position = md.Allpositions.objects.create(**data)
            
            return Response({"message":"ok", "position_id": position.id},status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def put(self, request, *args, **kwargs):
        try:
            user = request.user
            incoming = request.data 
            position_id = incoming.get("id")
            
            if not position_id:
                return Response({"message": "Position ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
            position = md.Allpositions.objects.filter(id=position_id, user = user.id).first()
            if not position:
                return Response({"message": "Position not found"}, status=status.HTTP_404_NOT_FOUND)
            
            for key, value in incoming.items():
                if hasattr(position, key):
                    setattr(position, key, value)
            position.save()
            return Response({"message": "Position updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            


class getholding(GenericAPIView):
    
    
    authentication_classes= (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            user = request.user

            # dash=utility(user)

            # oid=dash.getholding()
            data = md.allholding.objects.filter(user=user.id).values('nickname','broker','tradingsymbol','quantity','T1quantity','averageprice','ltp','profitandloss')
            
            


            return Response({"message":data})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)
            
    def post(self, request):
        try:
            user = request.user
            data = request.data
            # dash=utility(user)
            # oid=dash.getholding()
            
            print("Incomingssss holdingsssssss", data)
            
            data['user'] = user.id 
            holding = md.allholding.objects.create(**data)
            return Response({"message":"ok", "holding_id": holding.id},status=status.HTTP_200_OK)
           
        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        
        try:

            user = request.user
            incomming = request.data
            holding_id = incomming.get('id')
            
            if not holding_id:
                return Response({"message": "Holding ID required"}, status=status.HTTP_400_BAD_REQUEST)
            
           
            holding = md.allholding.objects.filter(id=holding_id, user = user.id).first()
            if not holding:
                return Response({"message": "Holding not found"}, status=status.HTTP_404_NOT_FOUND)
            
            for key, value in incomming.items():
                if hasattr(holding, key):
                    setattr(holding, key, value)
            holding.save()

            logger.info('Holding updated')
            
                

                
            return Response(
                {"Message": "Successfully Updated Holding"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)

class GetLogs(GenericAPIView):
    serializer_class = ser.LogSerializer

    def get(self, request):
        try:
            account_no = request.GET.get('account_no') or request.GET.get('accountnumber')

            logs_qs = md.LogEntry.objects.all().order_by('-updated_at')

            if not logs_qs.exists():
                sample_logs = [
                    {
                        'type': 'SYSTEM',
                        'description': 'Sample system initialization log',
                        'severity': 'INFO',
                        'accountnumber': '0001',
                    },
                    {
                        'type': 'TRADE',
                        'description': 'Sample trade executed: BUY 10 ABC',
                        'severity': 'DEBUG',
                        'accountnumber': '0001',
                    },
                    {
                        'type': 'USER',
                        'description': 'Sample user action: created watchlist',
                        'severity': 'WARNING',
                        'accountnumber': '0002',
                    },
                ]
                for item in sample_logs:
                    try:
                        md.LogEntry.objects.create(**item)
                    except Exception as e:
                        
                        print("Error creating sample log entry:", e)

                
                logs_qs = md.LogEntry.objects.all().order_by('-updated_at')

            if account_no:
                logs_qs = logs_qs.filter(accountnumber=account_no)

            serializer = self.get_serializer(logs_qs, many=True)
            return Response({"message": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error in getlogs:", e)
            logger.error(traceback.format_exc())
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

# @method_decorator(csrf_exempt, name='dispatch')

def verify_account_token(access_token):
    
    try:
        token_verification = verify_token(access_token)

        if (not token_verification.get('valid')) or (datetime.datetime.fromtimestamp(token_verification.get('exp'), tz=pytz.timezone("UTC")) < datetime.datetime.now(tz=pytz.timezone("UTC"))):
            return False, None, f"Invalid token: {token_verification.get('error')}"
        broker = md.Broker.objects.filter(accountnumber=token_verification['accountno']).last()
        if broker:
            
            return True,broker , None
        else:
            return False, None, "invalid broker"

            
      
    except Exception as e:
        logger.error(f"Error in verify_account_token: {e}")
        logger.error(traceback.format_exc())
        return False, None, str(e)



class publicorderdata(GenericAPIView):
   
    permission_classes = (AllowAny,)
    
    def post(self, request):
        try:
            accountnumber = request.data.get('AUTH_KEY')
            # auth_token = request.data.get('auth_token')
  
            is_valid, broker, error_msg = verify_account_token(accountnumber)
            if not is_valid:
                logger.warning(f"Unauthorized order data request: {error_msg}")
                return Response({
                    "message": error_msg, "code": status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)
            data = request.data.get('data')
            print(data)
            if data:

                md.orderstatus.objects.filter(accountnumber=broker.accountnumber).delete()
                for i in data:

                    order_data = {
                    'user': broker.user,
                    'broker': broker.brokername,
                    'accountnumber': broker.accountnumber,
                        'nickname': broker.nickname,
                        'tradingsymbol': i.get('ticker',''),
                        'exchange': i.get('listingExchange',''),
                        'instrument': i.get('secType',''),
                        'symboltoken': i.get('conid'),
                        'ordertype': i.get('origOrderType'),
                        'transactiontype': i.get('side'),
                        'product_type': i.get('product_type'),
                        'quantity': i.get('remainingQuantity'),
                        'price': i.get('price') if i.get('price') !='' else 0,
                        'avg_price': i.get('avgPrice'),
                        'orderid': i.get('orderId'),
                        'orderstatus': i.get('status', 'PENDING'),
                        'filledqty': i.get('filledQuantity', 0),
                        'side':i.get('side'),
                        'remarks': i.get('remarks', ''),
                        'lotsize': i.get('lotsize',''),
                        'lastmodifiedtime':datetime.datetime.strptime(i.get('lastExecutionTime', ''), '%y%m%d%H%M%S')

                        
                        ,}
                    
                    position = md.orderstatus.objects.create(**order_data)
                    logger.info(f"order status updated via public API - Account: {broker.accountnumber}")
                
                return Response({
                                "message": "Position created successfully",
                                "position_id": position.id
                            }, status=status.HTTP_201_CREATED)
            else:
                orderd= md.orderstatus.objects.filter(accountnumber=broker.accountnumber)
                if orderd:
                    # orderd.delete()
                    pass
                return Response({
                                "message": "order not posted since it is blank",
                            }, status=status.HTTP_201_CREATED)



                
            
        except Exception as e:
            print(e)
            logger.error(f"Error in PublicOrderDataAPI: {e}")
            logger.error(traceback.format_exc())
            return Response({
                "message": str(e),
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)





class publicpositiondata(GenericAPIView):
    
    permission_classes = (AllowAny,)
    
    def post(self, request):
        try:
            accountnumber = request.data.get('AUTH_KEY')
            # auth_token = request.data.get('auth_token')

            is_valid, broker, error_msg = verify_account_token(accountnumber)
            
            if not is_valid:
                logger.warning(f"Unauthorized position data request: {error_msg}")
                return Response({
                    "message": error_msg,
                    "code": status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            data = request.data.get('data')
            print(data)
            md.Allpositions.objects.filter(accountnumber=broker.accountnumber).delete()
            for i in data:
            # Extract position data
                position_data = {
                    'user': broker.user,
                    'broker': broker.brokername,
                    'nickname': broker.nickname,
                    'symboltoken':i.get('conid'),
                    'accountnumber':i.get('acctId'),
                    'tradingsymbol': i.get('contractDesc'),
                    'exchange':i.get('exchs'),
                    'netqty': i.get('position', 0),
                    'buyavgprice': i.get('avgPrice', 0),
                    'sellavgprice': i.get('sellavgprice', 0),
                    'ltp': i.get('mktPrice', 0),
                    'realised': i.get('realizedPnl', 0),
                    'unrealised': i.get('unrealizedPnl', 0),
                }

                position = md.Allpositions.objects.create(**position_data)

                logger.info(f"Position status updated via public API - Account: {broker.accountnumber}")
            return Response({
                        "message": "Position created successfully",
                        "position_id": position.id
                    }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(e)
            logger.error(f"Error in PublicPositionDataAPI: {e}")
            logger.error(traceback.format_exc())
            return Response({
                "message": str(e),
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)


class publicholdingdata(GenericAPIView):
    
    permission_classes = (AllowAny,)
    
    def post(self, request):
        try:
            accountnumber = request.data.get('AUTH_KEY')
            # auth_token = request.data.get('auth_token')
            
            is_valid, broker, error_msg = verify_account_token(accountnumber)
            
            if not is_valid:
                logger.warning(f"Unauthorized holdings data request: {error_msg}")
                return Response({
                    "message": error_msg,
                    "code": status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)
                
            data = request.data.get('data')
            for i in data:

                holdings_data = {
                    'user': broker.user,
                    'broker': broker.brokername,
                    'nickname': broker.nickname,
                    'tradingsymbol': i.get('tradingsymbol'),
                    'quantity': i.get('quantity', 0),
                    'T1quantity': i.get('T1quantity', 0),
                    'averageprice': i.get('averageprice', 0),
                    'ltp': i.get('ltp', 0),
                    'profitandloss': i.get('profitandloss', 0),
                }

            # holdings_data = {k: v for k, v in holdings_data.items() if v is not None}
            
                existing_holding = md.allholding.objects.filter(
                    user=broker.user,
                    broker=broker.brokername,
                    tradingsymbol=holdings_data.get('tradingsymbol')
                ).last()

                if existing_holding:

                    for key, value in holdings_data.items():
                        setattr(existing_holding, key, value)
                    existing_holding.save()

                    logger.info(f"Holding updated via public API - Account: {broker.accountnumber}")

                    return Response({
                        "message": "Holding updated successfully",
                        "holding_id": existing_holding.id
                    }, status=status.HTTP_200_OK)
                else:
                    holding = md.allholding.objects.create(**holdings_data)

                    logger.info(f"Holding created via public API - Account: {broker.accountnumber}, ")

                    return Response({
                        "message": "Holding created successfully",
                        "holding_id": holding.id
                    }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error in PublicHoldingsDataAPI: {e}")
            logger.error(traceback.format_exc())
            return Response({
                "message": str(e),
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)


class getpublicplaceorder(GenericAPIView):
    permissions_classes = (AllowAny,)
    
    def get(self, request):
        try:
            # auth_token = request.GET.get('auth_token')

            is_valid, broker, error_msg = verify_account_token(request.GET.get('AUTH_KEY'))
            print(is_valid,broker,error_msg)
            if not is_valid:
                logger.warning(f"Unauthorized place order request: {error_msg}")
                return Response({
                    "message": error_msg,
                    "code": status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            orders_qs = md.orderobject.objects.filter(
                user=broker.user,
                accountnumber=broker.accountnumber,
                active = True
                ).last()
            
            if orders_qs:
                order = ser.orderobject(instance=orders_qs)
                order= order.data
                
                orders_qs.active= False
                orders_qs.save()
            else:
                orders_qs=[]
                order=[]
            
            
            
            
            
         
            
            return Response({
                "message": "Place order data retrieved successfully",
                "accountnumber": broker.accountnumber,
                "orders": order
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in PublicPlaceOrderAPI: {e}")
            logger.error(traceback.format_exc())
            return Response({
                "message": str(e),
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
            
            
    def post(self,request):
        try:
            is_valid, broker, error_msg = verify_account_token(request.data.get('AUTH_KEY'))
        
            if not is_valid:
                logger.warning(f"Unauthorized place order request: {error_msg}")
                return Response({
                    "message": error_msg,
                    "code": status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)
            data = request.data.get('data')
            print(data)
            objectres= data.get("orders")
            objecidid= objectres['id']
            orders_qs = md.orderobject.objects.filter(
                id=objecidid).last()
            if orders_qs:
                orders_qs.orderstatus = data.get('status')
                orders_qs.remarks= data.get('remarks')
                orders_qs.orderid= data.get('orderid')
                orders_qs.save()
          
            
            
            
            
        
            return Response({
                "message": "Place order data retrieved successfully",
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in PublicPlaceOrderAPI: {e}")
            logger.error(traceback.format_exc())
            return Response({
                "message": str(e),
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
            

        
            
# @method_decorator(csrf_exempt, name='dispatch')           
class getforlogs(GenericAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            accountnumber = request.data.get('AUTH_KEY')
            # auth_token = request.data.get('auth_token')

            is_valid, broker, error_msg = verify_account_token(accountnumber)
            
            if not is_valid:
                print(f"Unauthorized get logs request: {error_msg}")
                return Response({
                    "message": error_msg,
                    "code": status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            logpath= f"{path}/Botlogs/public/{broker.accountnumber}"
            # print(request.data)
            log_path = os.path.join(logpath, request.data.get('data')['filename'])
            if not os.path.exists(log_path):
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
            log_path= os.path.normpath(log_path)
            with open(log_path, "w", encoding="utf-8") as f:
                    f.write(request.data.get('data')['content'])
                    f.close()
            broker.filename= request.data.get('data')['filename']
            broker.save()


            return Response({"message": "file updated and created "}, status=status.HTTP_200_OK)
            


               
           
            
        except Exception as e:
            print(f"Error in PublicGetLogsAPI: {e}")
            print(traceback.format_exc())
            return Response({
                "message": str(e),
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
        

class publicgetfunds(GenericAPIView):
    permissions_classes = (AllowAny,)
    def post(self, request):
        try:
            accountnumber = request.data.get('AUTH_KEY')
            # auth_token = request.data.get('auth_token')

            is_valid, broker, error_msg = verify_account_token(accountnumber)
            
            if not is_valid:
                print(f"Unauthorized get logs request: {error_msg}")
                return Response({
                    "message": error_msg,
                    "code": status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)

            
            incoming = request.data
            print("Incomingssss fundssssss", incoming['data'].keys())
            print(incoming['data']['lookaheadexcessliquidity']['amount'])
            funds_value = incoming['data']['lookaheadexcessliquidity']['amount']

            broker.funds = funds_value
            broker.save()

            return Response({"message": "Funds updated successfully", "brokerid": broker.brokerid}, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

            


class DownloadLogsAPI(GenericAPIView):
    authentication_classes= (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    

    def post(self, request):
        try:
            brokerid = request.data.get('brokerid')
            print(brokerid,'broker id ')
            broker = md.Broker.objects.filter(brokerid=brokerid).last()
            print(broker.accountnumber)
            if not broker:
                return Response({
                    "message": "Broker not found",
                    "code": status.HTTP_404_NOT_FOUND
                }, status=status.HTTP_404_NOT_FOUND)

            logpath = f"{path}/Botlogs/public/{broker.accountnumber}"
            
            if not broker.filename:
                return Response({
                    "message": "No log file available for this broker",
                    "code": status.HTTP_404_NOT_FOUND
                }, status=status.HTTP_404_NOT_FOUND)
            
            log_path = os.path.join(logpath, broker.filename)
            log_path = os.path.normpath(log_path)
            
            if not os.path.exists(log_path):
                return Response({
                    "message": "Log file not found on server",
                    "code": status.HTTP_404_NOT_FOUND
                }, status=status.HTTP_404_NOT_FOUND)

            filename = os.path.basename(log_path)
            filehandle = open(log_path, 'rb')
            response = FileResponse(filehandle, content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except Exception as e:
            print(f"Error in DownloadLogsAPI: {e}")
            print(traceback.format_exc())
            return Response({
                "message": str(e),
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
class orderrequest(GenericAPIView):
    # Token auth disabled to allow unauthenticated POSTs
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, *args, **kwargs):
        try:
            finaldata= []
            users = request.user
            data = dict()
            start= datetime.datetime.now(tz= pytz.timezone('Asia/Kolkata')).replace(hour=23, minute=59, second=0, microsecond=0)
            end = start- datetime.timedelta(days=1)
            print(end,start)
            # dash=utility(users)
            
            # dash.orderstatus()

            data = list(md.orderobject.objects.filter(user=users.id,updated_at__range=(end,start))  .order_by('-updated_at').values('id','accountnumber','transactiontype','tradingsymbol','orderstatus','remarks','quantity','avg_price',
                                                                      'ordertype','exchange','instrument','OUTSIDERTH','TIF','orderid','updated_at'))
            

            return Response({"message":data})

        except Exception as e:
            print(e)
            return Response({
                    "message": [],
                    "code": status.HTTP_400_BAD_REQUEST
                },  
                status=status.HTTP_400_BAD_REQUEST)


class getpubliccancel(GenericAPIView):
    permissions_classes = (AllowAny,)
    
    def post(self, request):
        try:
            # auth_token = request.GET.get('auth_token')

            is_valid, broker, error_msg = verify_account_token(request.data.get('AUTH_KEY'))
            print(is_valid,broker,error_msg)
            if not is_valid:
                logger.warning(f"Unauthorized place order request: {error_msg}")
                return Response({
                    "message": error_msg,
                    "code": status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            orders_qs = md.ordercancel.objects.filter(
                accountnumber=broker.accountnumber,
                cancel_order = True).last()
            if orders_qs:
                order = ser.ordercancel(instance=orders_qs)
                order= order.data
                
                orders_qs.cancel_order= False
                orders_qs.save()
            else:
                orders_qs=[]
                order=[]
            
            
            
   
            
            return Response({
                "message": "cancel order data retrieved successfully",
                "accountnumber": broker.accountnumber,
                "orders": order
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            logger.error(f"Error in getpubliccancel: {e}")
            logger.error(traceback.format_exc())
            return Response({
                "message": str(e),
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)
            
class getpublicmodify(GenericAPIView):
    permissions_classes = (AllowAny,)
    
    def post(self, request):
        try:
            # auth_token = request.GET.get('auth_token')

            is_valid, broker, error_msg = verify_account_token(request.data.get('AUTH_KEY'))
            print(is_valid,broker,error_msg)
            if not is_valid:
                logger.warning(f"Unauthorized place order request: {error_msg}")
                return Response({
                    "message": error_msg,
                    "code": status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            orders_qs = md.ordermodify.objects.filter(
                accountnumber=broker.accountnumber,
                modify_order = True).last()
            print(orders_qs,'orders_qs')
            if orders_qs:
                order = ser.ordermodify(instance=orders_qs)
                order= order.data
                
                orders_qs.modify_order= False
                orders_qs.save()
            else:
                orders_qs=[]
                order=[]
            
            
            
   
            
            return Response({
                "message": "Modify order data retrieved successfully",
                "accountnumber": broker.accountnumber,
                "orders": order
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            logger.error(f"Error in getpubliccancel: {e}")
            logger.error(traceback.format_exc())
            return Response({
                "message": str(e),
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

class getpubliconnection(GenericAPIView):
    permissions_classes = (AllowAny,)
    
    def post(self, request):
        try:
            # auth_token = request.GET.get('auth_token')

            is_valid, broker, error_msg = verify_account_token(request.data.get('AUTH_KEY'))
            if not is_valid:
                broker.status= False
                logger.warning(f"Unauthorized place order request: {error_msg}")
                return Response({
                    "message": error_msg,
                    "code": status.HTTP_401_UNAUTHORIZED
                }, status=status.HTTP_401_UNAUTHORIZED)
            broker.status = request.data['data']
            broker.save()
            
            
            
   
            
            return Response({
                "message": "Modify order data retrieved successfully",
            
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(e)
            logger.error(f"Error in getpubliccancel: {e}")
            logger.error(traceback.format_exc())
            return Response({
                "message": str(e),
                "code": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST)

