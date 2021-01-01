from django.db import models
from datetime import date
from django.contrib.auth.models import User

class TruncatingCharField(models.CharField):
    def get_prep_value(self, value):
        value = super(TruncatingCharField,self).get_prep_value(value)
        if value:
            return value[:self.max_length]
        return value

# Create your models here.
class NewLedger(models.Model):
    user_id = models.AutoField(primary_key=True)
    full_name = TruncatingCharField(max_length=50)
    primary_contact = TruncatingCharField(max_length=13)
    secondary_contact = TruncatingCharField(max_length=13, blank=True)
    address = TruncatingCharField(max_length=50)
    remark = TruncatingCharField(max_length=50)
    acc_status = models.BooleanField(default=True)

    total_amount = models.PositiveIntegerField(default=0)
    pending_amount = models.PositiveIntegerField(default=0)
    recieved_amount = models.PositiveIntegerField(default=0)
    temp_pending =models.PositiveIntegerField(default=0)
    temp_extra = models.PositiveIntegerField(default=0)
    monthly_installment = models.PositiveIntegerField(default=0)
    installment_status = models.BooleanField( default=False)
    

    def __str__(self):
        return str(self.user_id)
    class Meta:
        ordering = ['user_id']

class SubLedger(models.Model):
    sub_name = TruncatingCharField(max_length=50)
    account_number = TruncatingCharField(max_length=12)
    opening_date = TruncatingCharField(max_length=12)
    closing_date = TruncatingCharField(max_length=12)
    installment=models.PositiveIntegerField()
    total_amount = models.PositiveIntegerField()
    status = models.BooleanField( default=True)
    new_ledger_id = models.ForeignKey(NewLedger, on_delete=models.CASCADE)

    def __str__(self):
        return self.account_number

    class Meta:
        ordering = ['new_ledger_id']



class MakeReceipt(models.Model):
    ledger_no = models.ForeignKey(NewLedger, on_delete=models.CASCADE)
    installment_payment = models.PositiveIntegerField()
    receipt_date = models.DateField(default=date.today)
    remark = TruncatingCharField(max_length=50, blank=True, default=None)
    
    def __str__(self):
        return str(self.ledger_no)

    class Meta:
        ordering = ['receipt_date']
