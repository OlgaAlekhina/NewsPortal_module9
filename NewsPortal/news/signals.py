from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .models import Post, Category

@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers(instance, action, pk_set, *args, **kwargs):
    if action == 'post_add':
        html_content = render_to_string(
            'post_created_letter.html',
            {'post': instance}
        )
        for pk in pk_set:
            category = Category.objects.get(pk=pk)
            recipients = [user.email for user in category.subscribers.all()]
            msg = EmailMultiAlternatives(
                subject=f'рецепт курицы',
                from_email='olga-olechka-5@yandex.ru',
                to=recipients
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()