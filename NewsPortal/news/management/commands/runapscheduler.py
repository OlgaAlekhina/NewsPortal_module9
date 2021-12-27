import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from datetime import datetime, timedelta
from news.models import Category, Post
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def my_job():
    from_date = datetime.now() - timedelta(days=7)
    for cat in Category.objects.all():
        posts = Post.objects.filter(categories=cat).filter(post_time__gte=from_date)
        if posts.exists():
            recipients = [user.email for user in cat.subscribers.all()]
            msg = EmailMultiAlternatives(
                subject=f'Статьи за прошедшую неделю в категории "{cat.name}"',
                from_email='olga-olechka-5@yandex.ru',
                to=recipients
            )

            html_content = render_to_string(
                'weekly_mail.html',
                {'posts': posts})

            msg.attach_alternative(html_content, "text/html")

            msg.send()


def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="mon", hour="15", minute="00"),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
