import uuid
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from inventorymanager.common.utils.qrutils import generate_qr
from mediamanager.models import QRMedia


class Product(models.Model):
    object_id = models.UUIDField(unique=True, editable=False,
                                 default=uuid.uuid4, verbose_name='Public identifier')
    name = models.CharField(max_length=50)
    quantity = models.FloatField()
    price = models.FloatField()
    minstock = models.FloatField()
    qr = models.ForeignKey(QRMedia, related_name='%(app_label)s_%(class)s_qr_media',
                                    db_index=True, on_delete=models.CASCADE,null=True, blank=True)
class StockLog(models.Model):
    object_id = models.UUIDField(unique=True, editable=False,
                                 default=uuid.uuid4, verbose_name='Public identifier')
    product = models.ForeignKey(Product, related_name='%(app_label)s_%(class)s_product',
                                    db_index=True, on_delete=models.SET_NULL,null=True, blank=True)
    quantity = models.FloatField()
    price = models.FloatField()
    prevquantity = models.FloatField(null=True)
    prevprice = models.FloatField(null=True)
    date = models.DateTimeField(auto_now_add=True, blank=True)


@receiver(post_save, sender=Product)
def action_created(instance,created, **kwargs):
    if created:
        img = generate_qr(instance.id)
        img_io = BytesIO()
        original_image = img
        x = 786
        original_image.save(img_io, format='JPEG', quality=100)
        img_content = ContentFile(img_io.getvalue(), f'{instance.object_id}.jpg')
        qr_media = QRMedia.objects.create(name=f'{instance.object_id}.jpg', image=img_content)
        instance.qr = qr_media
        qr_media.save()
        instance.save()