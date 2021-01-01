from django.urls import path
from . import views

urlpatterns = [
    path("", views.login, name="Login Page"),
    path("log_out", views.log_out, name="Log Out Page"),
    path("dashboard", views.dashboard, name="Dashboard"),
    path("new_ledger", views.new_ledger, name="New Ledger"),
    path("sub_ledger", views.sub_ledger, name="Sub Ledger"),
    path("ledger_detail", views.ledger_detail, name="Ledger Detail"),
    path("balance_enq", views.balance_enq, name="Balance Enquiry"),
    path("ledger_setting", views.ledger_setting, name="Ledger Setting"),
    path("close_account", views.close_account, name="Close Account"),
    path("success", views.success, name="Success Message"),
    path("validation", views.validation, name="Validate Ledger"),
    path("profile", views.profile, name="User Profile"),

]
