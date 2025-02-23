from django.db import models
from customer.models import Address
from users.models import User


class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    address = models.ForeignKey(Address, models.DO_NOTHING)
    email = models.CharField(max_length=50, blank=True, null=True)
    store_id = models.SmallIntegerField()
    active = models.BooleanField()
    username = models.CharField(max_length=16)
    password = models.CharField(max_length=40, blank=True, null=True)
    last_update = models.DateTimeField()
    picture = models.BinaryField(blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'staff'

    def __str__(self):
        return str(self.first_name + " " + self.last_name)


class Store(models.Model):
    store_id = models.AutoField(primary_key=True)
    manager_staff = models.OneToOneField(Staff, models.DO_NOTHING)
    address = models.ForeignKey(Address, models.DO_NOTHING)
    last_update = models.DateTimeField()

    class Meta:
        db_table = 'store'
