# from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.contrib.auth.hashers import check_password, make_password
# from .models import User
# from .serializers import UserSerializer
# from rest_framework_simplejwt.tokens import RefreshToken,TokenError
# from rest_framework.permissions import AllowAny


# def get_new_access_token(refresh_token_str):
#     try:
#         refresh = RefreshToken(refresh_token_str)
#         return str(refresh.access_token)
#     except TokenError:
#         return None

# # ---------------- REGISTER ----------------
# class RegisterView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         data = request.data.copy()
#         if "password" in data:
#             data["password"] = make_password(data["password"])
#         user = User.objects.create(**data)
#         return Response({
#             "message": "User registered successfully",
#             "user": UserSerializer(user).data
#         }, status=status.HTTP_201_CREATED)


# # ---------------- LOGIN ----------------

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny
# from rest_framework import status
# from django.contrib.auth.hashers import make_password
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.tokens import RefreshToken
# import ldap
# from django.conf import settings
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         # Frontend sends 'username' → backend maps to 'name'
#         name = request.data.get("username")
#         password = request.data.get("password")

#         if not name or not password:
#             return Response(
#                 {"error": "Username and password are required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Optional: append AD domain if not provided
#         if '@' not in name:
#             name_ad = f"{name}@qatarmedicalcenter.com"
#         else:
#             name_ad = name

#         # Helper to safely decode LDAP bytes to string
#         def decode_ldap_value(value):
#             if isinstance(value, bytes):
#                 return value.decode("utf-8", errors="ignore")
#             return value

#         # ---------- Try Active Directory Authentication ----------
#         if getattr(settings, "LDAP_AUTH", True):
#             try:
#                 ldap_server = "ldap://172.31.46.129:389"
#                 base_dn = "dc=qatarmedicalcenter,dc=com"
#                 ldap_client = ldap.initialize(ldap_server)
#                 ldap_client.set_option(ldap.OPT_REFERRALS, 0)

#                 # Try to bind (authenticate user)
#                 ldap_client.simple_bind_s(name_ad, password)

#                 # Fetch user info
#                 search_filter = f"(&(objectClass=user)(userPrincipalName={name_ad}))"
#                 attrs = ["displayName", "mail", "userPrincipalName"]
#                 result = ldap_client.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, attrs)
#                 user_info = result[0][1] if result else {}

#                 display_name = decode_ldap_value(
#                     user_info.get("displayName", [name.split('@')[0]])[0]
#                 )
#                 email = decode_ldap_value(
#                     user_info.get("mail", [name_ad])[0]
#                 )

#                 ldap_client.unbind_s()

#                 # Create or update local user record
#                 user, created = User.objects.get_or_create(
#                     name=name_ad,
#                     defaults={
#                         "email": email,
#                         "firstname": display_name,
#                         "password": make_password(password)
#                     }
#                 )

#                 if not created:
#                     updated = False
#                     if user.firstname != display_name:
#                         user.firstname = display_name
#                         updated = True
#                     if user.email != email:
#                         user.email = email
#                         updated = True
#                     if updated:
#                         user.save()

#                 # Generate JWT token
#                 refresh = RefreshToken.for_user(user)
#                 return Response(
#                     {
#                         "message": "Login successful (AD Authenticated)",
#                         "user": {
#                             "name": user.name,
#                             "email": user.email,
#                             "firstname": user.firstname,
#                         },
#                         "refresh": str(refresh),
#                         "access": str(refresh.access_token),
#                     },
#                     status=status.HTTP_200_OK,
#                 )

#             except ldap.INVALID_CREDENTIALS:
#                 pass  # fallback to local authentication
#             except ldap.SERVER_DOWN:
#                 return Response(
#                     {"error": "Active Directory server unavailable"},
#                     status=status.HTTP_503_SERVICE_UNAVAILABLE,
#                 )
#             except Exception as e:
#                 return Response(
#                     {"error": str(e)},
#                     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                 )

#         # ---------- Local Django Authentication ----------
#         user = authenticate(name=name, password=password)
#         if user:
#             refresh = RefreshToken.for_user(user)
#             return Response(
#                 {
#                     "message": "Login successful (Local Authenticated)",
#                     "user": {
#                         "name": user.name,
#                         "email": user.email,
#                         "firstname": getattr(user, "firstname", ""),
#                     },
#                     "refresh": str(refresh),
#                     "access": str(refresh.access_token),
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         # ---------- Invalid Credentials ----------
#         return Response(
#             {"error": "Invalid username or password"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )



# # class LoginView(APIView):
# #     permission_classes = [AllowAny]

# #     def post(self, request):
# #         username = request.data.get("username")  
# #         password = request.data.get("password")

# #         try:
# #             user = User.objects.get(name=username)
# #         except User.DoesNotExist:
# #             return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

# #         if check_password(password, user.password):
# #             # Generate tokens only on login
# #             refresh = RefreshToken.for_user(user)
# #             return Response({
# #                 "message": "Login successful",
# #                 "user": UserSerializer(user).data,
# #                 "refresh": str(refresh),
# #                 "access": str(refresh.access_token)
# #             }, status=status.HTTP_200_OK)
# #         else:
# #             return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)


# def decode_ldap_response(dic):
#     if isinstance(dic,bytes):
#         try:
#             return(dic.decode("utf-8"))
#         except:
#             return(dic)
#     elif isinstance(dic,dict):
#         for key in dic:
#             dic[key] = decode_ldap_response(dic[key])
#         return(dic)
#     elif isinstance(dic,list):
#         # new_l = []
#         # for e in dic:
#         #     new_l.append(decode_ldap_response((e)))
#         # return(new_l)
#         return decode_ldap_response(dic[0])
#     else:
#         return(dic)

# def ensure_domain_in_username(username):
#     domain = "@qatarmedicalcenter.com"
#     if domain not in username:
#         username += domain
#     return username


# import pprint
# import binascii  # For binary data conversion

# # Function to decode the LDAP dictionary properly
# def decode_ldap_data(data):
#     decoded_data = {}
    
#     for key, value in data.items():
#         if isinstance(value, list):
#             new_values = []
#             for v in value:
#                 if isinstance(v, bytes):
#                     try:
#                         new_values.append(v.decode('utf-8'))  # Try decoding as UTF-8
#                     except UnicodeDecodeError:
#                         new_values.append(binascii.hexlify(v).decode('utf-8'))  # Convert binary to hex
#                 else:
#                     new_values.append(v)
#             decoded_data[key] = new_values
#         elif isinstance(value, bytes):
#             try:
#                 decoded_data[key] = value.decode('utf-8')  # Try decoding as UTF-8
#             except UnicodeDecodeError:
#                 decoded_data[key] = binascii.hexlify(value).decode('utf-8')  # Convert binary to hex
#         else:
#             decoded_data[key] = value  # Keep non-byte values unchanged
    
#     return decoded_data

# # class adAuthentication(APIView):
# #     # authentication_classes = [] #disables authentication
# #     # permission_classes = [] #disables permission
# #     permission_classes = [AllowAny]  
# #     def post(self, request):
# #         data = request.data
# #         if 'username' not in request.data or request.data['username']=='':
# #             return Response({"status":error.context['error_code'],"message" : "username"+language.context[language.defaultLang]['missing'] },status=status.HTTP_200_OK)
# #         elif 'password' not in request.data or request.data['password']=='':
# #             return Response({"status":error.context['error_code'],"message" : "password"+language.context[language.defaultLang]['missing'] },status=status.HTTP_200_OK)
# #         else:
            
# #             import ldap
                    
# #             try:
# #                 request.data['username']=ensure_domain_in_username(request.data['username'])
# #                 ldap_client = ldap.initialize("ldap://172.31.46.129:389")
# #                 # perform a synchronous bind
# #                 ldap_client.set_option(ldap.OPT_REFERRALS, 0)
# #                 # ldap_client.simple_bind_s("{}@qatarmedicalcenter.com".format(attrs['loginname']), request.data['password'])
# #                 ldap_client.simple_bind_s((request.data['username']), request.data['password'])
# #                 base = "dc=qatarmedicalcenter,dc=com"
# #                 scope = ldap.SCOPE_SUBTREE
                
# #                 # filter ="(&(objectClass=user)(sAMAccountName=" + (attrs['loginname']) + "))"
# #                 filterString ="(&(objectClass=user)(userPrincipalName=" + (request.data['username']) + "))"
# #                 displ_attrs = ["*"]

# #                 r = ldap_client.search_s(base, scope, filterString,displ_attrs)
# #                 result=r[0][1]

# #                 userDetails=decode_ldap_data(result)
# #                 toResponse={"name":userDetails['name'][0],'email':userDetails['userPrincipalName'][0]}

# #                 # userDetails='success'

# #                 return Response({"status" : error.context['success_code'], "message":'Authentication success','user':toResponse}, status=status.HTTP_200_OK)

# #             except ldap.SERVER_DOWN as e:
# #                 return Response({'status': error.context['error_code'], "message" : "AD server is down"}, status=status.HTTP_200_OK)
# #             except ldap.INVALID_CREDENTIALS:
# #                 ldap_client.unbind()
# #                 return Response({'status': error.context['error_code'], "message" : "Incorrect username or password"}, status=status.HTTP_200_OK)

# from django.shortcuts import render
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.contrib.auth.hashers import check_password, make_password
# from django.contrib.auth import get_user_model
# from rest_framework.permissions import AllowAny
# from rest_framework_simplejwt.tokens import RefreshToken, TokenError
# from django.conf import settings
# import ldap
# import binascii

# from .serializers import UserSerializer

# User = get_user_model()


# # ---------------- Helper: Get New Access Token ----------------
# def get_new_access_token(refresh_token_str):
#     try:
#         refresh = RefreshToken(refresh_token_str)
#         return str(refresh.access_token)
#     except TokenError:
#         return None


# # ---------------- Helper: Decode LDAP Data ----------------
# def decode_ldap_data(data):
#     decoded_data = {}
#     for key, value in data.items():
#         if isinstance(value, list):
#             new_values = []
#             for v in value:
#                 if isinstance(v, bytes):
#                     try:
#                         new_values.append(v.decode('utf-8'))
#                     except UnicodeDecodeError:
#                         new_values.append(binascii.hexlify(v).decode('utf-8'))
#                 else:
#                     new_values.append(v)
#             decoded_data[key] = new_values
#         elif isinstance(value, bytes):
#             try:
#                 decoded_data[key] = value.decode('utf-8')
#             except UnicodeDecodeError:
#                 decoded_data[key] = binascii.hexlify(value).decode('utf-8')
#         else:
#             decoded_data[key] = value
#     return decoded_data


# # ---------------- Helper: Ensure Domain ----------------
# def ensure_domain_in_username(username):
#     domain = "@qatarmedicalcenter.com"
#     if domain not in username:
#         username += domain
#     return username


# # ---------------- REGISTER ----------------
# class RegisterView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         data = request.data.copy()
#         if "password" in data:
#             data["password"] = make_password(data["password"])
#         user = User.objects.create(**data)
#         return Response({
#             "message": "User registered successfully",
#             "user": UserSerializer(user).data
#         }, status=status.HTTP_201_CREATED)


# # ---------------- LOGIN ----------------
# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")

#         if not username or not password:
#             return Response(
#                 {"error": "Username and password are required"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         username_ad = ensure_domain_in_username(username)

#         # ============= Try LDAP Authentication First =============
#         try:
#             if getattr(settings, "LDAP_AUTH", True):
#                 ldap_server = "ldap://172.31.46.129:389"
#                 base_dn = "dc=qatarmedicalcenter,dc=com"
#                 ldap_client = ldap.initialize(ldap_server)
#                 ldap_client.set_option(ldap.OPT_REFERRALS, 0)
#                 ldap_client.simple_bind_s(username_ad, password)

#                 search_filter = f"(&(objectClass=user)(userPrincipalName={username_ad}))"
#                 attrs = ["displayName", "mail", "userPrincipalName"]
#                 result = ldap_client.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, attrs)
#                 user_info = result[0][1] if result else {}
#                 user_info = decode_ldap_data(user_info)

#                 display_name = user_info.get("displayName", [username.split('@')[0]])[0]
#                 email = user_info.get("mail", [username_ad])[0]

#                 ldap_client.unbind_s()

#                 user, created = User.objects.get_or_create(
#                     name=username_ad,
#                     defaults={
#                         "email": email,
#                         "firstname": display_name,
#                         "password": make_password(password),
#                     },
#                 )

#                 if not created:
#                     updated = False
#                     if user.firstname != display_name:
#                         user.firstname = display_name
#                         updated = True
#                     if user.email != email:
#                         user.email = email
#                         updated = True
#                     if updated:
#                         user.save()

#                 refresh = RefreshToken.for_user(user)
#                 return Response(
#                     {
#                         "message": "Login successful (AD Authenticated)",
#                         "user": {
#                             "name": user.name,
#                             "email": user.email,
#                             "firstname": user.firstname,
#                         },
#                         "refresh": str(refresh),
#                         "access": str(refresh.access_token),
#                     },
#                     status=status.HTTP_200_OK,
#                 )

#         except ldap.INVALID_CREDENTIALS:
#             pass
#         except ldap.SERVER_DOWN:
#             pass
#         except Exception as e:
#             print("LDAP error:", e)
#             pass

#         # ============= Local DB Authentication =============
#         try:
#             if "@" in username:
#                 user = User.objects.get(email=username)
#             else:
#                 user = User.objects.get(name=username)
#         except User.DoesNotExist:
#             return Response(
#                 {"error": "Invalid username or password"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         # Check if password is hashed or plain
#         if user.password and user.password.startswith("pbkdf2_sha256$"):
#             valid_password = check_password(password, user.password)
#         else:
#             valid_password = user.password == password

#         if valid_password:
#             # Re-hash plain password if necessary
#             if not user.password.startswith("pbkdf2_sha256$"):
#                 user.password = make_password(password)
#                 user.save(update_fields=["password"])

#             refresh = RefreshToken.for_user(user)
#             return Response(
#                 {
#                     "message": "Login successful (Local DB Authenticated)",
#                     "user": {
#                         "id": user.id,
#                         "name": user.name,
#                         "email": user.email,
#                         "firstname": user.firstname or "",
#                     },
#                     "refresh": str(refresh),
#                     "access": str(refresh.access_token),
#                 },
#                 status=status.HTTP_200_OK,
#             )
#         else:
#             return Response(
#                 {"error": "Invalid username or password"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
import ldap
import binascii
from django.core.mail import send_mail
import random
import string
from django.utils import timezone
from .models import User,UserLoginHistory
from Ticket.models import Entity,UserRoleMapping,TicketsMasterConfiguration
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import UntypedToken

User = get_user_model()

# Assuming your User model has a 'force_password_change' field. Add this to your model if not:
# force_password_change = models.BooleanField(default=False)

# Helper: Generate random password
def generate_random_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Helper: Ensure domain for AD login
def ensure_domain_in_username(username):
    domain = "@qatarmedicalcenter.com"
    if domain not in username:
        username += domain
    return username

# Helper: Decode LDAP data
def decode_ldap_data(data):
    decoded_data = {}
    for key, value in data.items():
        if isinstance(value, list):
            new_values = []
            for v in value:
                if isinstance(v, bytes):
                    try:
                        new_values.append(v.decode("utf-8"))
                    except UnicodeDecodeError:
                        new_values.append(binascii.hexlify(v).decode("utf-8"))
                else:
                    new_values.append(v)
            decoded_data[key] = new_values
        elif isinstance(value, bytes):
            try:
                decoded_data[key] = value.decode("utf-8")
            except UnicodeDecodeError:
                decoded_data[key] = binascii.hexlify(value).decode("utf-8")
        else:
            decoded_data[key] = value
    return decoded_data

# ---------------- LOGIN ----------------
import logging

logger = logging.getLogger(__name__)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        ip_address = request.META.get('REMOTE_ADDR')

        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        username_ad = ensure_domain_in_username(username)

        # --- Try LDAP Authentication ---
        try:
            if getattr(settings, "LDAP_AUTH", True):
                ldap_server = "ldap://172.31.46.129:389"
                base_dn = "dc=qatarmedicalcenter,dc=com"
                ldap_client = ldap.initialize(ldap_server)
                ldap_client.set_option(ldap.OPT_REFERRALS, 0)
                ldap_client.simple_bind_s(username_ad, password)

                search_filter = f"(&(objectClass=user)(userPrincipalName={username_ad}))"
                attrs = ["displayName", "mail", "userPrincipalName"]
                result = ldap_client.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, attrs)
                user_info = result[0][1] if result else {}
                user_info = decode_ldap_data(user_info)

                display_name = user_info.get("displayName", [username.split("@")[0]])[0]
                email = user_info.get("mail", [username_ad])[0]

                ldap_client.unbind_s()

                user, created = User.objects.get_or_create(
                    name=username_ad,
                    defaults={
                        "email": email,
                        "firstname": display_name,
                        "password": make_password(password),
                        "force_password_change": False,  # LDAP users don't need force change
                    },
                )
                if created:
                    # Ensure fields are set even if defaults
                    user.email = email
                    user.firstname = display_name
                    user.save(update_fields=['email', 'firstname'])
                UserLoginHistory.objects.create(
                    user=user,
                    ip_address=ip_address
                )
                # Fetch entities data if entities_ids exists and is non-empty
                entities = []
                entity_data = None
                if hasattr(user, 'entities_ids') and user.entities_ids:
                    for eid in user.entities_ids:
                        try:
                            ent = Entity.objects.get(id=eid)
                            logo_url = ent.logo.url if ent.logo else None
                            entities.append({
                                "id": ent.id,
                                "name": ent.name,
                                "display_name": getattr(ent, 'display_name', ent.name),
                                "logo": logo_url,
                            })
                        except Entity.DoesNotExist:
                            logger.warning(f"Entity ID {eid} not found for user {user.id}")
                            continue
                    entity_data = entities[0] if entities else None

                # Fetch roles data if roles_ids exists and is non-empty
                roles = []
                if hasattr(user, 'roles_ids') and user.roles_ids:
                    for rid in user.roles_ids:
                        try:
                            rol = TicketsMasterConfiguration.objects.get(id=rid)
                            roles.append({
                                "id": rol.id,
                                "name": rol.field_name,
                            })
                        except TicketsMasterConfiguration.DoesNotExist:
                            logger.warning(f"Role ID {rid} not found for user {user.id}")
                            continue
                else:
                    # Default role if no roles_ids
                    roles = [{"id": None, "name": "user"}]

                # Fetch UserRoleMapping data for the user
                mappings = UserRoleMapping.objects.filter(user=user).select_related('role', 'entity')
                role_mappings = [
                    {
                        "id": m.id,
                        "role_id": m.role.id,
                        "role_name": m.role.field_name,  # Assuming field_name is the display field for role
                        "entity_id": m.entity.id,
                        "entity_name": m.entity.name,
                        "created_date": m.created_date,
                        "updated_date": m.updated_date,
                    }
                    for m in mappings
                ]

                refresh = RefreshToken.for_user(user)
                response_data = {
                    "message": "Login successful (AD Authenticated)",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email,
                        "firstname": user.firstname or display_name,
                        "entities": entities,
                        "roles": roles,
                        "entities_ids": user.entities_ids or [],
                        "roles_ids": getattr(user, 'roles_ids', []) or [],
                        "entity_data": entity_data,
                        "role_mappings": role_mappings,  # Added UserRoleMapping data
                    },
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "force_change": user.force_password_change,
                }
                logger.info(f"Login Response Entity Data: {entity_data}")
                logger.info(f"Login Response Role Mappings: {role_mappings}")
                return Response(response_data, status=status.HTTP_200_OK)
        except ldap.INVALID_CREDENTIALS:
            pass
        except ldap.SERVER_DOWN:
            pass
        except Exception as e:
            print("LDAP error:", e)
            pass

        # --- Local DB Authentication ---
        try:
            user = User.objects.get(email=username) if "@" in username else User.objects.get(name=username)
        except User.DoesNotExist:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

        valid_password = check_password(password, user.password) if user.password.startswith("pbkdf2_sha256$") else user.password == password

        if valid_password:
            if not user.password.startswith("pbkdf2_sha256$"):
                user.password = make_password(password)
                user.save(update_fields=["password"])
            UserLoginHistory.objects.create(
                user=user,
                ip_address=ip_address
            )
            # Fetch entities data if entities_ids exists and is non-empty
            entities = []
            entity_data = None
            if hasattr(user, 'entities_ids') and user.entities_ids:
                for eid in user.entities_ids:
                    try:
                        ent = Entity.objects.get(id=eid)
                        logo_url = ent.logo.url if ent.logo else None
                        entities.append({
                            "id": ent.id,
                            "name": ent.name,
                            "display_name": getattr(ent, 'display_name', ent.name),
                            "logo": logo_url,
                        })
                    except Entity.DoesNotExist:
                        logger.warning(f"Entity ID {eid} not found for user {user.id}")
                        continue
                entity_data = entities[0] if entities else None

            # Fetch roles data if roles_ids exists and is non-empty
            roles = []
            if hasattr(user, 'roles_ids') and user.roles_ids:
                for rid in user.roles_ids:
                    try:
                        rol = TicketsMasterConfiguration.objects.get(id=rid)
                        roles.append({
                            "id": rol.id,
                            "name": rol.field_name,
                        })
                    except TicketsMasterConfiguration.DoesNotExist:
                        logger.warning(f"Role ID {rid} not found for user {user.id}")
                        continue
            else:
                # Default role if no roles_ids
                roles = [{"id": None, "name": "user"}]

            # Fetch UserRoleMapping data for the user
            mappings = UserRoleMapping.objects.filter(user=user).select_related('role', 'entity')
            role_mappings = [
                {
                    "id": m.id,
                    "role_id": m.role.id,
                    "role_name": m.role.field_name,  # Assuming field_name is the display field for role
                    "entity_id": m.entity.id,
                    "entity_name": m.entity.name,
                    "created_date": m.created_date,
                    "updated_date": m.updated_date,
                }
                for m in mappings
            ]

            refresh = RefreshToken.for_user(user)
            response_data = {
                "message": "Login successful (Local DB Authenticated)",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "firstname": user.firstname or "",
                    "entities": entities,
                    "roles": roles,
                    "entities_ids": user.entities_ids or [],
                    "roles_ids": getattr(user, 'roles_ids', []) or [],
                    "entity_data": entity_data,
                    "role_mappings": role_mappings,  # Added UserRoleMapping data
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "force_change": user.force_password_change,
            }
            logger.info(f"Login Response Entity Data: {entity_data}")
            logger.info(f"Login Response Role Mappings: {role_mappings}")
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

# class LogoutView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user

#         # 1. Save logout_time — THIS IS THE MAIN GOAL
#         latest_login = UserLoginHistory.objects.filter(
#             user=user,
#             logout_time__isnull=True
#         ).order_by('-login_time').first()

#         if latest_login:
#             latest_login.logout_time = timezone.now()
#             latest_login.save(update_fields=['logout_time'])
#             # Optional: debug log
#             print(f"Logout time saved: {latest_login.logout_time} for user {user}")

#         # 2. Optional: Blacklist refresh token (recommended for security)
#         refresh_token = request.data.get("refresh")
#         if refresh_token:
#             try:
#                 token = RefreshToken(refresh_token)
#                 token.blacklist()
#                 print(f"Refresh token blacklisted for user {user}")
#             except TokenError as e:
#                 print(f"Token blacklisting failed (already used/expired): {e}")
#             except Exception as e:
#                 print(f"Unexpected error during blacklist: {e}")

#         return Response({"message": "Logged out successfully"}, status=200)
class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=400)

        user_id = None

        # Step 1: Try to extract user_id EVEN from expired/invalid tokens
        try:
            # This works even if token is expired
            
            untyped = UntypedToken(refresh_token)
            user_id = untyped.payload.get("user_id")
        except Exception as e:
            print(f"Could not extract user_id from token: {e}")

        # Step 2: ALWAYS save logout_time if we know the user
        if user_id:
            latest_login = UserLoginHistory.objects.filter(
                user_id=user_id,
                logout_time__isnull=True
            ).order_by('-login_time').first()

            if latest_login:
                latest_login.logout_time = timezone.now()
                latest_login.save(update_fields=['logout_time'])
                print(f"Logout time saved for user {user_id}: {latest_login.logout_time}")

        # Step 3: Try to blacklist (but NEVER fail the logout because of it)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            print(f"Refresh token blacklisted for user {user_id or 'unknown'}")
        except (TokenError, InvalidToken, Exception) as e:
            print(f"Blacklist failed (not critical): {e}")

        # ALWAYS return success — user is logged out locally anyway
        return Response({"message": "Logged out successfully"}, status=200)
# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request):
#         username = request.data.get("username")
#         password = request.data.get("password")

#         if not username or not password:
#             return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

#         username_ad = ensure_domain_in_username(username)

#         # --- Try LDAP Authentication ---
#         is_ldap_auth = False
#         try:
#             if getattr(settings, "LDAP_AUTH", True):
#                 ldap_server = "ldap://172.31.46.129:389"
#                 base_dn = "dc=qatarmedicalcenter,dc=com"
#                 ldap_client = ldap.initialize(ldap_server)
#                 ldap_client.set_option(ldap.OPT_REFERRALS, 0)
#                 ldap_client.simple_bind_s(username_ad, password)

#                 search_filter = f"(&(objectClass=user)(userPrincipalName={username_ad}))"
#                 attrs = ["displayName", "mail", "userPrincipalName"]
#                 result = ldap_client.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, attrs)
#                 user_info = result[0][1] if result else {}
#                 user_info = decode_ldap_data(user_info)

#                 display_name = user_info.get("displayName", [username.split("@")[0]])[0]
#                 email = user_info.get("mail", [username_ad])[0]

#                 ldap_client.unbind_s()

#                 user, created = User.objects.get_or_create(
#                     name=username_ad,
#                     defaults={
#                         "email": email,
#                         "firstname": display_name,
#                         "password": make_password(password),
#                         "force_password_change": False,  # LDAP users don't need force change
#                         "is_ldap_user": True,  # Add this field to User model if needed to flag LDAP
#                     },
#                 )
#                 is_ldap_auth = True

#                 # --- Fetch user-entity-role mappings ---
#                 mappings = UserRoleMapping.objects.filter(user=user).select_related('entity')
#                 entities = []
#                 for mapping in mappings:
#                     entity_obj = mapping.entity
#                     logo_url = entity_obj.logo.url if entity_obj.logo else None
#                     # Ensure only primitives: avoid any model instances or QuerySets
#                     entity_data = {
#                         "id": int(entity_obj.id),
#                         "name": str(entity_obj.name),
#                         "display_name": str(safe_getattr(entity_obj, 'display_name', entity_obj.name)),
#                         "logo": str(logo_url) if logo_url else None,
#                         "role": str(mapping.role),
#                         # If tickets_count is needed (assuming reverse relation to a Ticket model, not TicketsMasterConfiguration):
#                         # "tickets_count": entity_obj.tickets.count() if hasattr(entity_obj, 'tickets') else 0,
#                         # But if 'tickets' relates to TicketsMasterConfiguration, use explicit query:
#                         # tickets_count = 0  # Or query separately: TicketsMasterConfiguration.objects.filter(entity=entity_obj).count()
#                         # "tickets_count": tickets_count,
#                     }
#                     entities.append(entity_data)

#                 primary_entity_data = entities[0] if entities else None

#                 refresh = RefreshToken.for_user(user)
#                 response_data = {
#                     "message": "Login successful (AD Authenticated)",
#                     "user": {
#                         "id": int(user.id),
#                         "name": str(user.name),
#                         "email": str(user.email),
#                         "firstname": str(user.firstname),
#                         "is_ldap_user": bool(user.is_ldap_user),
#                         "entities": entities,  # List of entity-role mappings (primitives only)
#                         "primary_entity": primary_entity_data,
#                     },
#                     "refresh": str(refresh),
#                     "access": str(refresh.access_token),
#                     "force_change": bool(user.force_password_change),
#                 }
#                 logger.info(f"Login Response Entities: {entities}, Primary: {primary_entity_data}")
#                 return Response(response_data, status=status.HTTP_200_OK)
#         except ldap.INVALID_CREDENTIALS:
#             pass
#         except ldap.SERVER_DOWN:
#             pass
#         except Exception as e:
#             print("LDAP error:", e)
#             pass

#         # --- Local DB Authentication ---
#         try:
#             user = User.objects.get(email=username) if "@" in username else User.objects.get(name=username)
#         except User.DoesNotExist:
#             return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

#         valid_password = check_password(password, user.password) if user.password.startswith("pbkdf2_sha256$") else user.password == password

#         if valid_password:
#             if not user.password.startswith("pbkdf2_sha256$"):
#                 user.password = make_password(password)
#                 user.save(update_fields=["password"])

#             # --- Fetch user-entity-role mappings ---
#             mappings = UserRoleMapping.objects.filter(user=user).select_related('entity')
#             entities = []
#             for mapping in mappings:
#                 entity_obj = mapping.entity
#                 logo_url = entity_obj.logo.url if entity_obj.logo else None
#                 # Ensure only primitives (same as above)
#                 entity_data = {
#                     "id": int(entity_obj.id),
#                     "name": str(entity_obj.name),
#                     "display_name": str(safe_getattr(entity_obj, 'display_name', entity_obj.name)),
#                     "logo": str(logo_url) if logo_url else None,
#                     "role": str(mapping.role),
#                     # Same as above for tickets_count if needed
#                 }
#                 entities.append(entity_data)

#             primary_entity_data = entities[0] if entities else None

#             refresh = RefreshToken.for_user(user)
#             response_data = {
#                 "message": "Login successful (Local DB Authenticated)",
#                 "user": {
#                     "id": int(user.id),
#                     "name": str(user.name),
#                     "email": str(user.email),
#                     "firstname": str(user.firstname or ""),
#                     "is_ldap_user": bool(getattr(user, 'is_ldap_user', False)),
#                     "entities": entities,
#                     "primary_entity": primary_entity_data,
#                 },
#                 "refresh": str(refresh),
#                 "access": str(refresh.access_token),
#                 "force_change": bool(user.force_password_change),
#             }
#             logger.info(f"Login Response Entities: {entities}, Primary: {primary_entity_data}")
#             return Response(response_data, status=status.HTTP_200_OK)
#         return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)
    
# ---------------- FORGOT PASSWORD ----------------
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "No user found with this email"}, status=status.HTTP_404_NOT_FOUND)

        new_password = generate_random_password()
        user.password = make_password(new_password)
        user.force_password_change = True  # Set flag to force change on next login
        user.save(update_fields=["password", "force_password_change"])

        try:
            send_mail(
                subject="Your New Password",
                message=f"Hello {user.firstname or user.name},\n\nYour temporary password is: {new_password}\nPlease login and change it immediately for security.",
                from_email="no-reply@qatarmedicalcenter.com",
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "A new temporary password has been sent to your email. Please change it after login."}, status=status.HTTP_200_OK)
    
# ---------------- CHANGE PASSWORD ----------------
# class ChangePasswordView(APIView):
#     permission_classes = [IsAuthenticated]  # Require auth

#     def post(self, request):
#         user = request.user
#         old_password = request.data.get("old_password")
#         new_password = request.data.get("new_password")
#         confirm_password = request.data.get("confirm_password")

#         if not all([old_password, new_password, confirm_password]):
#             return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

#         if new_password != confirm_password:
#             return Response({"error": "New passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

#         # Verify old password
#         if not check_password(old_password, user.password):
#             return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

#         # Update password and reset force flag
#         user.password = make_password(new_password)
#         user.force_password_change = False
#         user.save(update_fields=["password", "force_password_change"])

#         return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # Handle both snake_case and camelCase
        old_password = request.data.get("old_password") or request.data.get("oldPassword")
        new_password = request.data.get("new_password") or request.data.get("newPassword")
        confirm_password = request.data.get("confirm_password") or request.data.get("confirmPassword")

        if not all([old_password, new_password, confirm_password]):
            missing = []
            if not old_password: missing.append("old_password")
            if not new_password: missing.append("new_password")
            if not confirm_password: missing.append("confirm_password")
            return Response(
                {"error": f"Missing fields: {', '.join(missing)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password != confirm_password:
            return Response(
                {"error": "New passwords do not match"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify old password
        if not check_password(old_password, user.password):
            return Response(
                {"error": "Old password is incorrect"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update password and reset force flag
        user.password = make_password(new_password)
        user.force_password_change = False
        user.save(update_fields=["password", "force_password_change"])

        return Response(
            {"message": "Password changed successfully"}, 
            status=status.HTTP_200_OK
        )