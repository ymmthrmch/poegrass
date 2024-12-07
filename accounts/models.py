from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

class UserManager(BaseUserManager):

    def _create_user(self, email, account_id, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email,account_id=account_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_user(self, email, account_id, password, **extra_fields):
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_member',False)
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(
            email=email,
            account_id=account_id,
            password=password,
            **extra_fields,
            )
    
    def create_memberuser(self, email, account_id, password, **extra_fields):
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_member',True)
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(
            email=email,
            account_id=account_id,
            password=password,
            **extra_fields,
            )
    
    def create_staff(self, email, account_id, password, **extra_fields):
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_member',True)
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(
            email=email,
            account_id=account_id,
            password=password,
            **extra_fields,
            )
    
    def create_superuser(self, email, account_id, password, **extra_fields):
        extra_fields.setdefault('is_active',True)
        extra_fields.setdefault('is_member',True)
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        return self._create_user(
            email=email,
            account_id=account_id,
            password=password,
            **extra_fields,
            )

class User(AbstractBaseUser,PermissionsMixin):
    account_id=models.CharField(
        verbose_name="アカウントid",
        unique=True,
        max_length=17,
        null=False,
        blank=False,
        validators=[
            RegexValidator(
                r'^[a-zA-Z0-9_]+$', "半角英数字、アンダーラインのみ使用できます。"
                )
        ]
    )
    email=models.EmailField(
        verbose_name="メールアドレス",
        null=False,
        blank=False,
        unique=True
    )
    first_name=models.CharField(
        verbose_name="名前",
        null=True,
        blank=False,
        max_length=50
    )
    last_name=models.CharField(
        verbose_name="姓（空欄可）",
        null=True,
        blank=True,
        max_length=50
    )
    is_active=models.BooleanField(
        verbose_name="active",
        default=True
    )
    is_member=models.BooleanField(
        verbose_name="member",
        default=False
    )
    is_staff=models.BooleanField(
        verbose_name="staff",
        default=False
    )
    is_superuser=models.BooleanField(
        verbose_name="superuser",
        default=False
    )
    bio=models.TextField(
        verbose_name="自己紹介",
        max_length=140,
        null=True,
        blank=True
    )
    created_at=models.DateTimeField(
        verbose_name="アカウント作成日",
        auto_now_add=True
    )
    updated_at=models.DateTimeField(
        verbose_name="更新日",
        auto_now=True
    )

    objects = UserManager()

    USERNAME_FIELD = 'account_id' # ログイン時、ユーザー名の代わりにaccount_idを使用
    REQUIRED_FIELDS = ['email']  # スーパーユーザー作成時に設定する項目

    def __str__(self):
        return self.account_id