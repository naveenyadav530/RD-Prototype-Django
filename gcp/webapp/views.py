from django.shortcuts import render, redirect
from django.contrib import messages
import re
from .models import NewLedger, SubLedger, MakeReceipt
from django.contrib.auth.models import User, auth
from .decorators import authenticated_user, staff_user, super_user
# Create your views here.

from datetime import date


def profile(request):
    if request.method == "POST":
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        if new_password == confirm_password:
            try:
                result = request.user
                u = User.objects.get(username=result.username)
                u.set_password(new_password)
                u.save()
                return redirect("/")
            except:
                messages.error(request, "Technical Error Accourd")
                return redirect("/profile")

        else:

            messages.error(request, "Password Does not match")
            return redirect("/profile")
    else:
        try:
            result = request.user
            table = {"full_name":User.objects.first, "email_id":result.email, "username":result.username}
            return render(request, "profile.html", table)
        except Exception as e:
            messages.error(request, str(e))
            return redirect("/profile")

def log_out(request):
    auth.logout(request)
    return redirect("/")

@authenticated_user
def login(request):    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        value = auth.authenticate(username=username, password= password)
        if value is not None:
            auth.login(request, value)
            return redirect("/dashboard")
        else:
            messages.error(request, "Invalid Credentials")
            return redirect("/")     
    else:
        return render(request, "login.html")

@staff_user
def dashboard(request):
    if request.method =="POST" and "search" in request.POST:
        try:
            user_id = request.POST["ledger_no"]
            result = NewLedger.objects.get(pk=user_id, acc_status=True)
            table = NewLedger.objects.filter(installment_status=False, acc_status=True)
            if result.installment_status:
                if result.temp_pending:
                    total_payment = result.temp_pending
                else:
                    total_payment = 0
            else:
                total_payment= result.monthly_installment+result.temp_pending -result.temp_extra
            information = {"data":result,"table":table,"usr_id":user_id, "total_payment":total_payment}
            return render(request, "dashboard.html", information)
        except:
            messages.error(request,"Invalid Ledger Number")
            return redirect("/dashboard")

    elif request.method =="POST" and "generate" in request.POST:
        user_id = request.POST["ledger_no"]
        payment = request.POST["installment"]
        remark = request.POST["addon"]
        try:
            result = NewLedger.objects.get(pk=user_id, acc_status=True)
        except:
            messages.error(request,"Invalid Ledger Number")
            return redirect("/dashboard")

        try:
            payment = int(payment)
        except:
            messages.error(request,"Invalid payment amount")
            return redirect("/dashboard")
        
        if payment < 0:
            messages.error(request,"Invalid payment amount")
            return redirect("/dashboard")


            
        try:
            if result.installment_status:
                if result.temp_pending ==0 and result.temp_extra == 0:
                    result.temp_extra = result.temp_extra + payment
                    result.recieved_amount = result.recieved_amount + payment
                    result.pending_amount = result.pending_amount - payment
                    result.save()
                    
                    data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                    data.save()
                    return redirect("/success")
                elif result.temp_pending > 0:
                    amount = payment - result.temp_pending
                    if amount > 0:
                        result.temp_extra = payment - result.temp_pending
                        result.temp_pending = 0
                        result.recieved_amount = result.recieved_amount + payment
                        result.pending_amount = result.pending_amount - payment
                        result.save()
                        data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                        data.save()
                        return redirect("/success")
                    elif amount == 0: 
                        result.temp_pending = 0
                        result.recieved_amount = result.recieved_amount + payment
                        result.pending_amount = result.pending_amount - payment
                        result.save()
                        data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                        data.save()
                        return redirect("/success")
                    elif amount < 0:
                        result.temp_pending = result.temp_pending - payment
                        result.recieved_amount = result.recieved_amount + payment
                        result.pending_amount = result.pending_amount - payment
                        result.save()
                        data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                        data.save()
                        return redirect("/success")
                elif result.temp_extra > 0:
                    result.temp_extra = payment + result.temp_extra
                    result.recieved_amount = result.recieved_amount + payment
                    result.pending_amount = result.pending_amount - payment
                    result.save()
                    data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                    data.save()
                    return redirect("/success")
            else:
                if result.temp_pending == 0 and result.temp_extra == 0:
                    if payment == result.monthly_installment:
                        result.installment_status = True
                        result.recieved_amount = result.recieved_amount + payment
                        result.pending_amount = result.pending_amount - payment
                        result.save()
                        data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                        data.save()
                        return redirect("/success")
                    elif payment >result.monthly_installment:
                        result.installment_status = True
                        result.temp_extra = payment - result.monthly_installment
                        result.recieved_amount = result.recieved_amount + payment
                        result.pending_amount = result.pending_amount - payment
                        result.save()
                        data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                        data.save()
                        return redirect("/success")
                    
                    elif payment < result.monthly_installment:
                        result.installment_status = True
                        result.temp_pending = result.monthly_installment - payment
                        result.recieved_amount = result.recieved_amount + payment
                        result.pending_amount = result.pending_amount - payment
                        result.save()
                        data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                        data.save()
                        return redirect("/success")
                    
                elif result.temp_pending > 0:
                    if payment == result.monthly_installment:
                        result.installment_status = True
                        result.recieved_amount = result.recieved_amount + payment
                        result.pending_amount = result.pending_amount - payment
                        result.save()
                        data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                        data.save()
                        return redirect("/success")
                    elif payment > result.monthly_installment:
                        result.installment_status = True
                        amount = payment-result.monthly_installment
                        if amount > result.temp_pending:
                            result.temp_extra = amount - result.temp_pending
                            result.temp_pending = 0
                            result.recieved_amount = result.recieved_amount + payment
                            result.pending_amount = result.pending_amount - payment
                            result.save()
                            data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                            data.save()
                            return redirect("/success")
                        elif amount == result.temp_pending:
                            result.temp_pending = 0
                            result.temp_extra = 0
                            result.recieved_amount = result.recieved_amount + payment
                            result.pending_amount = result.pending_amount - payment
                            result.save()
                            data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                            data.save()
                            return redirect("/success")
                        elif amount < result.temp_pending:
                            result.temp_pending = result.temp_pending - amount
                            result.recieved_amount = result.recieved_amount + payment
                            result.pending_amount = result.pending_amount - payment
                            result.save()
                            data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                            data.save()
                            return redirect("/success") 
                    elif payment < result.monthly_installment:
                        result.installment_status = True
                        result.temp_pending = (result.monthly_installment - payment)+ result.temp_pending
                        result.recieved_amount = result.recieved_amount + payment
                        result.pending_amount = result.pending_amount - payment
                        result.save()
                        data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                        data.save()
                        return redirect("/success") 

                elif result.temp_extra > 0:
                    if payment == result.monthly_installment:
                        result.installment_status = True
                        result.recieved_amount = result.recieved_amount + payment
                        result.pending_amount = result.pending_amount - payment
                        result.save()
                        data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                        data.save()
                        return redirect("/success")
                    elif payment > result.monthly_installment:
                        result.installment_status = True
                        result.temp_extra = (payment-result.monthly_installment)+ result.temp_extra
                        result.recieved_amount = result.recieved_amount + payment
                        result.pending_amount = result.pending_amount - payment
                        result.save()
                        data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                        data.save()
                        return redirect("/success")
                    elif payment < result.monthly_installment:
                        print("welcome")
                        result.installment_status = True
                        amount = result.monthly_installment - payment
                        print(amount)
                        if amount == result.temp_extra:
                            print(amount)
                            result.temp_extra = 0
                            result.temp_pending = 0
                            result.recieved_amount = result.recieved_amount + payment
                            result.pending_amount = result.pending_amount - payment
                            result.save()
                            data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                            data.save()
                            return redirect("/success")
                        elif amount > result.temp_extra:
                            print("2 elif")
                            result.temp_pending = amount - result.temp_extra
                            result.temp_extra = 0
                            result.recieved_amount = result.recieved_amount + payment
                            result.pending_amount = result.pending_amount - payment
                            result.save()
                            data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                            data.save()
                            return redirect("/success")
                        elif amount < result.temp_extra:
                            print("3rd elif")
                            result.temp_extra = result.temp_extra - amount
                            result.recieved_amount = result.recieved_amount + payment
                            result.pending_amount = result.pending_amount - payment
                            result.save()
                            data = MakeReceipt.objects.create(ledger_no=result, remark=remark, installment_payment=payment)
                            data.save()
                            return redirect("/success")
            return redirect("/dashboard")
        except Exception as e:
            messages.error(request, str(e))
            return redirect("/dashboard")
    else:

        pending_result = NewLedger.objects.filter(installment_status=False, acc_status=True)
        return render(request, "dashboard.html", {"table":pending_result})



@staff_user
def success(request):
    return render(request, "success.html")

# create new ledger
@staff_user
def new_ledger(request):
    if request.method == "POST":
        full_name = request.POST['full_name']
        primary_contact = request.POST['primary_contact']
        address = request.POST['address']
        secondary_contact = request.POST['secondary_contact']
        remark = request.POST['remark']
        Pattern = re.compile(r"^\+(?:[0-9] ?){6,14}[0-9]$")
        
        # validation
        primary_contact = "+91"+primary_contact

        if len(secondary_contact) ==0:
            if Pattern.match(primary_contact):
                try:
                    result = NewLedger.objects.create(full_name=full_name, address=address, primary_contact=primary_contact, secondary_contact=secondary_contact, remark=remark)
                    result.save()
                    return redirect("/success")
                    
                except:
                    messages.error(request, "Error accured to save Ledger")
                    return redirect("/new_ledger")
            else:
                messages.error(request, "Invalid Primary Contact Number")
                return redirect("/new_ledger")   
        elif Pattern.match("+91"+secondary_contact):
            if Pattern.match(primary_contact):
                try:
                    result = NewLedger.objects.create(full_name=full_name, address=address, primary_contact=primary_contact, secondary_contact="+91"+secondary_contact, remark=remark)
                    result.save()
                    return redirect("/success")
                except:
                    messages.error(request, "Error accured to save Ledger")
                    return redirect("/new_ledger")
            else:
                messages.error(request, "Invalid Primary Contact Number")
                return redirect("/new_ledger")  
        else:
            messages.error(request, "Invalid Secondary Contact Number")
            return redirect("/new_ledger")  
  
    else:
        table = NewLedger.objects.filter(acc_status=True)
        return render(request, "new_ledger.html", {"table":table})

    
# create sub ledger
@staff_user
def sub_ledger(request):
    if request.method =="POST" and "search" in request.POST:
        try:
            user_id = request.POST['user_id']
            result = NewLedger.objects.get(user_id= user_id, acc_status=True)
            table = SubLedger.objects.filter(status=True)
            return render(request, "sub_ledger.html", {"success":result.full_name+" from "+result.address, "value":user_id, "table":table})
            
        except:
            messages.error(request, "Invalid Ledger Number")
            return redirect("/sub_ledger")
            
        
    elif request.method =="POST" and "create" in request.POST:
        user_id = request.POST['user_id']
        name = request.POST['sub_name']
        account_number = request.POST['acc_no']
        opening_date = request.POST['opening_date']
        installment = request.POST['installment']
        if not name:
            messages.error(request, "Sub Ledger Name Field Can't be Empty.")
            return redirect("/sub_ledger")
        elif not account_number:
            messages.error(request, "Account Number Can't be Empty.")
            return redirect("/sub_ledger")
        elif not opening_date:
            messages.error(request, "Select Valid Opening Date.")
            return redirect("/sub_ledger")
        elif not installment:
            messages.error(request, "Monthly Installment Can't be Empty.")
            return redirect("/sub_ledger") 
        else:
            try:
                installment = int(installment)
            except:
                messages.error(request, "Invalid Monthly Installment")
                return redirect("/sub_ledger")
            
            try:
                date =opening_date.split("-")
                closing_year = int(date[0]) +5
                closing_date = str(closing_year)+"-"+date[1]+"-"+date[2]
            except:
                messages.error(request, "Check Your Opening Date")
                return redirect("/sub_ledger")
            
            

            try:    
                ledger_result = NewLedger.objects.get(pk=user_id,acc_status=True)            
                # save sub Ledger
                result = SubLedger.objects.create(new_ledger_id=ledger_result, total_amount=installment*60,installment=installment, sub_name=name, account_number=account_number, opening_date=opening_date,closing_date=closing_date)
                result.save()
                # update Data
                
                ledger_result.total_amount = ledger_result.total_amount + (installment*60)
                ledger_result.pending_amount = ledger_result.pending_amount + (installment*60)
                ledger_result.monthly_installment = ledger_result.monthly_installment + installment
                ledger_result.save()
                return redirect("/success")
            except:
                messages.error(request, "Unable to Create Sub Ledger")
                return redirect("/sub_ledger")
            
    else:
        table = SubLedger.objects.filter(status=True)
        return render(request, "sub_ledger.html", {"table":table})  


# validation Page
@super_user
def validation(request):
    if request.method =="POST" and "update_month" in request.POST:  
        val = date.today()
        if val.day == 1 or val == 2:
            
            data = NewLedger.objects.filter(acc_status=True)
            for result in data:
                if result.installment_status:
                    result.installment_status =False
                    result.save()
                else:
                    if result.temp_extra ==0 and result.temp_pending ==0:
                        result.temp_pending = result.monthly_installment
                        result.save()     
                    elif result.temp_extra >0:
                        amount = result.monthly_installment - result.temp_extra
                        if amount == 0:
                            
                            result.temp_extra = 0
                            result.temp_pending = 0
                            result.save()
                        
                        elif amount >0:
                           
                            result.temp_extra = 0
                            result.temp_pending =  amount
                            result.save()
                        else:
                            result.temp_extra = abs(result.temp_extra - result.monthly_installment)
                            
                            result.temp_pending = 0
                            result.save()     
                    elif result.temp_pending >0:
                        result.temp_pending = result.temp_pending + result.monthly_installment
                        result.save() 

            return redirect("/success")                  
        else:
            message = "You Can Only Perform Action on 1st and 2nd Day of Month."
            messages.error(request, message )
            return redirect("/validation")
    else:
        try:
            result = NewLedger.objects.filter(acc_status=True)
            return render(request, "validation.html", {"table":result})
        except:
            messages.error("Technical Error!.")
            return render(request, "validation.html")


# Ledger Details
@staff_user
def ledger_detail(request):
    if request.method=="POST" and "ledger_no" in request.POST:
        ledger = request.POST["ledger"]
        if not ledger:
            messages.error(request, "Ledger Field Can't be Empty")
            return redirect("/ledger_detail")
        else:
            try:
                ledger = int(ledger)
            except:
                messages.error(request, "Enter a valid Ledger No.")
                return redirect("/ledger_detail")
            
            try:
                result = SubLedger.objects.filter(status=True, new_ledger_id=ledger)
                data = MakeReceipt.objects.filter(ledger_no=str(ledger))
                information = {"table1":result, "table2":data, "search_value":ledger}
                return render(request, "ledger_detail.html", information)
            except:
                messages.error(request, "No Record Found")
                return redirect("/ledger_detail")        
    return render(request, "ledger_detail.html")



@staff_user
def balance_enq(request):
    try:
        data = NewLedger.objects.filter(acc_status=True)
        total_amount = 0
        total_received = 0
        total_pending = 0
        for value in data:
            total_amount = value.total_amount + total_amount
            total_received = value.recieved_amount + total_received
            total_pending = value.pending_amount + total_pending
    except:
        messages.error(request, "Technical Error.....")
        return redirect("/balance_enq")
    
    table = {"table":data, "total_amount":total_amount, "total_received":total_received, "total_pending":total_pending}
    return render(request, "balance_enq.html", table)



@staff_user
def ledger_setting(request):
    if request.method=="POST" and "search" in request.POST:
        ledger = request.POST["ledger"]
        try:
            ledger = int(ledger)
        except:
            messages.error(request, "Enter a valid Ledger No.")
            return redirect("/ledger_setting")
            
        try:
            data = NewLedger.objects.get(user_id = ledger)
            result = SubLedger.objects.filter(status=True, new_ledger_id=ledger)
            information = {"table":result,"new_ledger":data}
            return render(request, "ledger_setting.html", information)
        except:
            messages.error(request, "No Record Found")
            return redirect("/ledger_setting")
   
    elif request.method == "POST" and "name_update" in request.POST:
        ledger =request.POST["ledger"]
        name = request.POST["full_name"]
        if not name:
            messages.error(request, "Enter full name")
            return redirect("/ledger_setting")
        else:
            try:
                data = NewLedger.objects.get(user_id=ledger)
                data.full_name = name
                data.save()
                return redirect("/success")
            except:
                messages.error(request, "Technical Error")
                return redirect("/ledger_setting")
    
    elif request.method =="POST" and "address_update" in request.POST:
        ledger = request.POST["ledger"]
        address = request.POST["address"]
        if not address:
            messages.error(request, "Enter Address")
            return redirect("/ledger_setting")
        else:
            try:
                data = NewLedger.objects.get(user_id=ledger)
                data.address = address
                data.save()
                return redirect("/success")
            except:
                messages.error(request, "Technical Error")
                return redirect("/ledger_setting")
    
    elif request.method =="POST" and "primary_update" in request.POST:
        ledger = request.POST["ledger"]
        primary = request.POST["primary_contact"]
        Pattern = re.compile(r"^\+(?:[0-9] ?){6,14}[0-9]$")
         
        if not primary:
            messages.error(request, "Enter Mobile Number")
            return redirect("/ledger_setting")
        else:
            primary_contact = "+91"+primary
            if Pattern.match(primary_contact):
                try:
                    data = NewLedger.objects.get(user_id=ledger)
                    data.primary_contact = primary_contact
                    data.save()
                    return redirect("/success")
                except:
                    messages.error(request, "Technical Error")
                    return redirect("/ledger_setting")
            else:
                messages.error(request, "Enter Valid Contact Number")
                return redirect("/ledger_setting")
    elif request.method =="POST" and "secondary_update" in request.POST:
        ledger = request.POST["ledger"]
        primary = request.POST["secondary_contact"]
        Pattern = re.compile(r"^\+(?:[0-9] ?){6,14}[0-9]$")
         
        if not primary:
            messages.error(request, "Enter Mobile Number")
            return redirect("/ledger_setting")
        else:
            primary_contact = "+91"+primary
            if Pattern.match(primary_contact):
                try:
                    data = NewLedger.objects.get(user_id=ledger)
                    data.secondary_contact = primary_contact
                    data.save()
                    return redirect("/success")
                except:
                    messages.error(request, "Technical Error")
                    return redirect("/ledger_setting")
            else:
                messages.error(request, "Enter Valid Contact Number")
                return redirect("/ledger_setting")

    elif request.method =="POST" and "delete_account" in request.POST:
        ledger = request.POST["ledger"]
        result = NewLedger.objects.get(user_id=ledger)
        result.acc_status = False
        result.save()
        return redirect("/success")

    elif request.method =="POST" and "delete_acc" in request.POST:
        acc_number = request.POST["acc_number"]
        try:
            result = SubLedger.objects.get(account_number=acc_number, status=True)
            if result.closing_date <= str(date.today()):
                result.status=False
                result.save()
                return redirect("/success")
            else:
                messages.error(request, "Can't delete before closing date")
                return render(request, "ledger_setting.html")
        except:
            messages.error(request, "Account Number Not Found")
            return redirect("/ledger_setting")
            
    
    elif request.method =="POST" and "update_acc" in request.POST:
    
        acc_number1 = request.POST["acc_no1"]
        acc_number2 = request.POST["acc_no2"]
        try:
            result = SubLedger.objects.get(account_number=acc_number1, status=True)
            result.account_number = acc_number2
            result.save()
            return redirect("/success")
        except:
            messages.error(request, "Account Number Not Found")
            return redirect("/ledger_setting")
    
    else:
        return render(request, "ledger_setting.html")


@staff_user
def close_account(request):
    if request.method=="POST" and "delete_ledger" in request.POST:
        ledger = request.POST["ledger_no"]
        try:
            ledger_result = NewLedger.objects.get(pk=ledger)
            if ledger_result.acc_status:
                messages.error(request, "Account is Open Can't Delete.")
                return redirect("/close_account")
            else:
                ledger_result.delete()
                return redirect("/success")
        except:
            messages.error(request, "Check Your Ledger No.")
            return redirect("/close_account")
       
    
    elif request.method=="POST" and "delete_sub" in request.POST:
        acc_no = request.POST["acc_no"]
        try:
            result = SubLedger.objects.get(account_number=acc_no)
            if result.status:
                messages.error(request, "Sub Ledger Open Can't Delete")
                return redirect("/close_account")
            else:
                result.delete()
                return redirect("/success")
        except:
            messages.error(request, "Check Your Account No.")
            return redirect("/close_account")
        
    
    
    else:
        try:
            result=NewLedger.objects.filter(acc_status=False)
            data=SubLedger.objects.filter(status=False)
            return render(request, "close_account.html", {"table":result, "table1":data})
        except:
            messages.error(request, "Technical Error.")
            return redirect("/close_account")
        return render(request, "close_account.html")

