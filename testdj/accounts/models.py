from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

AVATAR_CHOICES = [
    ('🐍', 'Питон'),
    ('🎮', 'Геймер'),
    ('🧠', 'Data‑science'),
    ('🚀', 'Ракета'),
    ('🍕', 'Пицца'),
]


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.CharField(
        max_length=2,
        choices=AVATAR_CHOICES,
        default='🐍',
    )
    bio = models.TextField(blank=True, default='')
    balance = models.IntegerField(
        default=0,
        verbose_name='Баланс'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f'Профиль {self.user.username}'

    def add_balance(self, amount):
        """Добавить к балансу"""
        self.balance += int(amount)
        self.save()
        return self.balance

    def subtract_balance(self, amount):
        """Снять с баланса"""
        if self.balance >= int(amount):
            self.balance -= int(amount)
            self.save()
            return True
        return False

    def has_balance(self, amount):
        """Проверить достаточно ли баланса"""
        return self.balance >= int(amount)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, balance=0)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    profile, created = Profile.objects.get_or_create(user=instance)
    if not created:
        profile.save()
