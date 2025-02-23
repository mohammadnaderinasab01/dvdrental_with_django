from django.db import models
from store.models import Staff
from films.models import Film, Inventory
from customer.models import Customer


class Rental(models.Model):
    rental_id = models.AutoField(primary_key=True)
    rental_date = models.DateTimeField()
    inventory = models.ForeignKey(Inventory, models.DO_NOTHING)
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    return_date = models.DateTimeField(blank=True, null=True)
    staff = models.ForeignKey(Staff, models.DO_NOTHING)
    last_update = models.DateTimeField()

    class Meta:
        db_table = 'rental'
        unique_together = (('rental_date', 'inventory', 'customer'),)


class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    staff = models.ForeignKey(Staff, models.DO_NOTHING)
    rental = models.ForeignKey(Rental, models.DO_NOTHING)
    amount = models.DecimalField(max_digits=5, decimal_places=2)
    payment_date = models.DateTimeField()

    class Meta:
        db_table = 'payment'
