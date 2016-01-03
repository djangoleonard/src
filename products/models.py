from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.utils.text import slugify


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(active=True)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        # return self.get_queryset()
        return self.get_queryset().active()

    def get_related(self, instance):
        products_one = self.get_queryset().filter(categories__in=instance.categories.all())
        products_two = self.get_queryset().filter(default=instance.default)
        qs = (products_one | products_two).exclude(id=instance.id).distinct()
        return qs


class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    active = models.BooleanField(default=True)
    categories = models.ManyToManyField('Category', blank=True)
    default = models.ForeignKey('Category', related_name='default_category', null=True, blank=True)

    objects = ProductManager()

    class Meta:
        ordering = ["-title"]

    def __unicode__(self):   # def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"pk": self.pk})

    # def get_absolute_url(self):
    #     return "/products/%s" % self.pk


class Variation(models.Model):
    product = models.ForeignKey(Product)
    title = models.CharField(max_length=120)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    sale_price = models.DecimalField(decimal_places=2, max_digits=10, null=True, blank=True)
    active = models.BooleanField(default=True)
    inventory = models.IntegerField(null=True, blank=True)   # refer none == unlimited amount

    def __unicode__(self):
        return self.title

    def get_price(self):
        if self.sale_price is not None:
            return self.sale_price
        else:
            return self.price

    def get_absolute_url(self):
        return self.product.get_absolute_url()


def product_saved_receiver(sender, instance, created, *args, **kwargs):
    # print sender
    product = instance
    variations = product.variation_set.all()
    if variations.count() == 0:
        new_var = Variation()
        new_var.product = product
        new_var.title = "Default"
        new_var.price = product.price
        new_var.save()

    #  varations = Variation.objects.filter(product=product)

    # print instance
    # print created

post_save.connect(product_saved_receiver, sender=Product)

# Product Images


def image_upload_to(instance, filename):
    title = instance.product.title
    slug = slugify(title)
    # file_extension = filename.split(".")[1]
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" % (slug, instance.id, file_extension)
    return "products/%s/%s" % (slug, new_filename)


class ProductImage(models.Model):
    product = models.ForeignKey(Product)
    # image = models.ImageField(upload_to='products/')
    image = models.ImageField(upload_to=image_upload_to)

    def __unicode__(self):
        return self.product.title

# Product Category


class Category(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})


# class ProductCategories(models.Model):
#     product = models.OneToOneField(Product)
#     categories = models.ManyToManyField(Category)
#     default = models.ForeignKey(Category)
#
#     def __unicode__(self):
#         return self.product.title
