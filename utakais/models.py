from accounts.models import User
from datetime import datetime,timedelta
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from poegrass.utils import japanese_strftime

class Event(models.Model):
    title = models.CharField(
        verbose_name="タイトル",
        max_length=63,
        blank=True,
        )
    start_time = models.DateTimeField(
        verbose_name="開始時刻",
        default=timezone.now,
    )
    location = models.CharField(
        verbose_name="場所",
        blank=True,
        max_length=63,
        )
    organizer = models.ForeignKey(
        User,
        verbose_name="司会者",
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        )
    deadline = models.DateTimeField(
        verbose_name="提出締切",
        blank=True,
        null=True,
    )
    STATUS_CHOICES = [
        ('public', '公開'),
        ('limited', '限定公開'),
        ('private', '非公開'),
    ]
    ann_status = models.CharField(
        verbose_name="告知公開設定",
        max_length=7,
        choices=STATUS_CHOICES,
        default='public'
        )
    rec_status = models.CharField(
        verbose_name="記録公開設定",
        max_length=7,
        choices=STATUS_CHOICES,
        default='private'
    )
    ann_desc = models.TextField(
        verbose_name="告知説明",
        max_length=511,
        blank=True,
        null=True,
        )
    ended = models.BooleanField(
        verbose_name="終了済み",
        default=False,
    )
    rec_desc = models.TextField(
        verbose_name="記録説明",
        max_length=511,
        blank=True,
        null=True,
    )

    @property
    def ann_is_public(self):
        return self.ann_status == 'public'
    
    @property
    def ann_is_limited(self):
        return self.ann_status == 'limited'
    
    @property
    def ann_is_private(self):
        return self.ann_status == 'private'
    
    @property
    def rec_is_public(self):
        return self.rec_status == 'public'
    
    @property
    def rec_is_limited(self):
        return self.rec_status == 'limited'
    
    @property
    def rec_is_private(self):
        return self.rec_status == 'private'
    
    @property
    def is_past(self):
        now = timezone.now()
        return now > self.start_time
    
    def clean(self):
        if self.start_time and self.deadline:
            if self.start_time < self.deadline:
                raise ValidationError(
                    {'deadline': "提出締切は開始時刻よりも後ろにはできません。"}
                )
    
    def save(self, *args, **kwargs):
        if not self.title and self.start_time:
            date = self.start_time
            self.title = japanese_strftime(date, "%Y年%m月%d日（%a）の歌会")
        if not self.deadline and self.start_time:
            self.deadline = self.start_time - timedelta(hours=6)
        if not self.location:
            self.location = "未定"
        if self.is_past==True:
            self.is_ann_public = False
        super().save(*args, **kwargs)
            
    def __str__(self):
        return self.title

class Participant(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name="参加者",
        on_delete=models.CASCADE,
        )
    event = models.ForeignKey(
        Event,
        verbose_name="参加イベント",
        on_delete=models.CASCADE,
        )
    is_observer = models.BooleanField(
        verbose_name="見学者フラグ",
        default=False,
        )

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'event'], name='unique_user_event')
        ]

class Tanka(models.Model):
    content = models.TextField(
        verbose_name="詠草",
    )
    author = models.ForeignKey(
        User,
        verbose_name="作者",
        on_delete=models.CASCADE,
        )
    STATUS_CHOICES = [
        ('public', '公開'),
        ('limited', '限定公開'),
        ('private', '非公開'),
    ]
    status = models.CharField(
        verbose_name="公開設定",
        max_length=7,
        choices=STATUS_CHOICES,
        default='private'
        )
    created_at = models.DateTimeField(
        verbose_name="作成日時",
        auto_now_add=True,
    )

    @property
    def is_public(self):
        return self.status == 'public'
    
    @property
    def is_limited(self):
        return self.status == 'limited'
    
    @property
    def is_private(self):
        return self.status == 'private'
    
    def __str__(self):
        return self.content[:5] if self.content else ""

class TankaList(models.Model):
    title = models.CharField(
        verbose_name="タイトル",
        max_length=63,
    )
    owner = models.ForeignKey(
        User,
        verbose_name="作成者",
        on_delete=models.CASCADE,
    )
    tankas = models.ManyToManyField(
        Tanka,
        verbose_name="短歌リスト",
        through='TankaListItem',
    )
    description = models.TextField(
        verbose_name="説明",
        max_length=127,
    )
    is_public = models.BooleanField(
        verbose_name="公開設定",
        default=True,
    )
    created_at = models.DateTimeField(
        verbose_name="作成日時",
        auto_now_add=True,
    )

    def add_tanka(self, tanka):
        if not self.tankalistitem_set.filter(tanka=tanka).exists():
            last_order = self.tankalistitem_set.aggregate(max_order=models.Max('order'))['max_order']
            new_order = (last_order or 0) + 1
            TankaListItem.objects.create(tanka_list=self,tanka=tanka,order=new_order)
        else:
            raise ValueError("この短歌は既に追加されています。")

    def __str__(self):
        return self.title
    
class TankaListItem(models.Model):
    tanka_list = models.ForeignKey(TankaList, on_delete=models.CASCADE)
    tanka = models.ForeignKey(Tanka, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()  # 順序を表すフィールド

    class Meta:
        ordering = ['order']  # orderフィールドに基づいて順序を並べ替え
        constraints = [
            models.UniqueConstraint(fields=['tanka_list', 'tanka'], name='unique_tanka_in_list')
        ]

    def __str__(self):
        return f'({self.order}){self.tanka.content[:5]}'
