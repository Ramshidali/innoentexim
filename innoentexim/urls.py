from django.contrib import admin
from django.views.static import serve
from django.urls import  include, path, re_path
from innoentexim import settings
from main import views as general_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('app/accounts/', include('registration.backends.default.urls')),
    
    path('',include(('main.urls'),namespace='main')), 
    path('super-admin/',general_views.app,name='app'),
    
    path('super-admin/sales/',include(('sales.urls'),namespace='sales')), 
    path('super-admin/profit/',include(('profit.urls'),namespace='profit')), 
    path('super-admin/purchase/',include(('purchase.urls'),namespace='purchase')), 
    path('super-admin/export/',include(('exporting.urls'),namespace='exporting')), 
    path('super-admin/core-team/',include(('coreteam.urls'),namespace='core_team')), 
    path('super-admin/directors/',include(('directors.urls'),namespace='directors')), 
    path('super-admin/investors/',include(('investors.urls'),namespace='investors')), 
    path('super-admin/executives/',include(('executieves.urls'),namespace='executive')), 
    path('super-admin/sales-party/',include(('sales_party.urls'),namespace='sales_party')), 
    path('super-admin/purchase-party/',include(('purchase_party.urls'),namespace='purchase_party')), 
    path('super-admin/other-expences/',include(('other_expences.urls'),namespace='other_expences')), 
    
    # api
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/auth/', include(('api.v1.authentication.urls','authentication'), namespace='api_v1_authentication')),
    path('api/v1/purchase/', include(('api.v1.purchase.urls','purchase'), namespace='api_v1_purchase')),
    path('api/v1/sales/', include(('api.v1.sales.urls','sales'), namespace='api_v1_sales')),
    path('api/v1/profit/', include(('api.v1.profit.urls','profit'), namespace='api_v1_profit')),
    path('api/v1/dashboard/', include(('api.v1.dashboard.urls','dashboard'), namespace='api_v1_dashboard')),
    
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
]
