"""
    modules.users.models
    ~~~~~~~~~~~~~~~~~~~~
    User models.
"""

# 3rd party
import sentry_sdk as sentry
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django_extensions.db.fields import (
    AutoSlugField, CreationDateTimeField, ModificationDateTimeField,
)


class UserManager(BaseUserManager):

    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        now = timezone.now()
        if not email:
            msg = 'A unique email is required.'
            raise ValueError(msg)
        email = self.normalize_email(email)
        user = self.model(
            email=email, is_staff=is_staff, is_active=True, is_superuser=is_superuser,
            last_login=now, date_joined=now, **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)

    def unconfirmed(self):
        return self.get_queryset().filter(
            last_login__isnull=True,
            confirmed_at__isnull=True,
        )


class User(AbstractBaseUser, PermissionsMixin):
    """
    We need a custom user model because Django wants usernames, and usernames are stupid.
    This custom user model is email/password only.

    Email and password are required. Other fields are optional.

    """
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    USERNAME_FIELD: str = 'email'
    REQUIRED_FIELDS: list = []

    email = models.EmailField(_('email address'), max_length=254, unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=255, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=255, blank=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Unsetting this should be used to deactivate a user instead of deleting them.'),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    confirmed_at = models.DateTimeField(_('confirmed at'), null=True)
    created_at = CreationDateTimeField()
    updated_at = ModificationDateTimeField()

    slug = AutoSlugField(
        allow_unicode=True, null=True, default=None, unique=True, db_index=True,
        populate_from=('first_name', 'last_name'),
    )

    phone_number = models.CharField(max_length=255, blank=False, null=True)

    objects = UserManager()

    @cached_property
    def full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        try:
            send_mail(subject, message, from_email, [self.email], **kwargs)
        except Exception as e:
            sentry.capture_exception(e)

    def __str__(self):
        if len(self.full_name) > 1:
            return '{} ({})'.format(self.full_name, self.email)
        return self.email

    def __repr__(self):
        return '<{} ({}): {} {}>'.format(
            self.__class__.__name__, self.id, self.full_name, self.email,
        )
