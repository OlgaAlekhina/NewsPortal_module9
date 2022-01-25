from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Author(models.Model):
    author = models.OneToOneField(User, on_delete=models.CASCADE)
    author_rating = models.FloatField(default=0.0)

    def __str__(self):
        return f'{self.author}'

    def update_rating(self):
        post_rating = self.post_set.all().values('post_rating')
        rating1 = sum(rate['post_rating'] for rate in post_rating) * 3

        user = self.author
        comment_rating = user.comment_set.all().values('comment_rating')
        rating2 = sum(rate['comment_rating'] for rate in comment_rating)

        author_posts = Post.objects.filter(post_author=self)
        rating3 = 0

        for post in author_posts:
            comment_rating2 = post.comment_set.all().values('comment_rating')
            s = sum(rate['comment_rating'] for rate in comment_rating2)
            rating3 += s

        self.author_rating = rating1 + rating2 + rating3
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    subscribers = models.ManyToManyField(User, related_name='subscribed_categories')

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return f'/news/category/{self.id}'


class Post(models.Model):
    article = 'ART'
    news = 'NEW'

    TYPES = [(article, 'Статья'), (news, 'Новость')]

    post_author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=3, choices=TYPES, default=article)
    post_time = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    post_title = models.CharField(max_length=250)
    post_text = models.TextField()
    post_rating = models.FloatField(default=0.0)

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        return f'{self.post_text[:124]}...'

    def __str__(self):
        return f'{self.post_title.title()}: {self.post_text[:50]}'

    def get_absolute_url(self):
        return f'/news/{self.id}'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment_text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    comment_rating = models.FloatField(default=0.0)

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        self.save()


