from django.conf import settings
from django.db import models


from carts.models import Cart


class UserCheckout(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True)             # optional
    email = models.EmailField(unique=True)
    # merchant_id

    def __unicode__(self):
        return self.email


ADDRESS_TYPE = (
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
)


class UserAddress(models.Model):
    user = models.ForeignKey(UserCheckout)
    type = models.CharField(max_length=120, choices=ADDRESS_TYPE)
    street = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    zipcode = models.CharField(max_length=120)

    def __unicode__(self):
        return self.street


class Order(models.Model):
    cart = models.ForeignKey(Cart)
    user = models.ForeignKey(UserCheckout)
    billing_address = models.ForeignKey(UserAddress, related_name='billing_address')
    shipping_address = models.ForeignKey(UserAddress, related_name='shipping_address')
    shipping_total_price = models.DecimalField(decimal_places=2, max_digits=15, default=5.99)
    order_total = models.DecimalField(decimal_places=2, max_digits=15, default=5.99)
    # order_id

    def __unicode__(self):
        return str(self.cart.id)

# class Order(models.Model):
#     # cart
#     # user not required
#     # quest not required
#     # shipping address
#     # billing address
#     # shipping total price
#     # order total (cart total + shipping)
#     # order_id -> custom id
