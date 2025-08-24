from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import RegexValidator


# Reuse these in serializers/admin
NIGERIAN_STATES = [
    'Abia','Adamawa','Akwa Ibom','Anambra','Bauchi','Bayelsa','Benue',
    'Borno','Cross River','Delta','Ebonyi','Edo','Ekiti','Enugu','FCT',
    'Gombe','Imo','Jigawa','Kaduna','Kano','Katsina','Kebbi','Kogi',
    'Kwara','Lagos','Nasarawa','Niger','Ogun','Ondo','Osun','Oyo',
    'Plateau','Rivers','Sokoto','Taraba','Yobe','Zamfara'
]

ROLE_CHOICES = [
    ('sitting-member', 'Sitting Member'),
    ('sitting-head', 'Sitting Head'),
    ('regional-sitting-head', 'Regional Sitting Head'),
]

whatsapp_validator = RegexValidator(
    regex=r'^\+234\d{10}$',
    message='WhatsApp must be +234 followed by 10 digits, e.g. +2348012345678.'
)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        if not extra_fields.get('username'):
            raise ValueError('Username is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)


    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='sitting-member')
    location = models.CharField(max_length=20, choices=[(s, s) for s in NIGERIAN_STATES], default="Unknown")
    whatsapp = models.CharField(max_length=14, validators=[whatsapp_validator])

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # shown when creating superuser

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        return self.email


# Personal To-Do Categories
PERSONAL_CATEGORIES = [
    ("strength", "Enhancing Strength"),
    ("weakness", "Limiting Weaknesses"),
    ("opportunity", "Tapping Opportunities"),
    ("threat", "Reducing/Overcoming Threats"),
]

class DefaultTodo(models.Model):
    """
    Default structured todo for sitting members
    """
    name = models.CharField(max_length=64)
    todo_type = models.CharField(max_length=32, choices=[
        ("checkbox", "Checkbox"),
        ("number", "Number"),
        ("text", "Text"),
    ], default="checkbox")
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    # optional field for tracking page numbers or counts
    extra_field_label = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name

class PersonalTodo(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="personal_todos")
    category = models.CharField(max_length=32, choices=PERSONAL_CATEGORIES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["completed", "-created_at"]

    def __str__(self):
        return f"[{self.category}] {self.title}"
