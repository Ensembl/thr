from django.conf import settings

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    This function allows every user to have an automatically generated Token
    More details about token authentication and signals:
    https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
    https://docs.djangoproject.com/en/3.1/ref/signals/#post-save
    :param sender: The model class
    :param instance: the actual instance being saved
    :param created: a boolean, True if a new record was created
    """
    if created:
        Token.objects.create(user=instance)
