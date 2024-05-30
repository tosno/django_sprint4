from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class PublishedPostsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True)


class BaseBlogModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.',
        verbose_name='Опубликовано',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено',
    )

    class Meta:
        abstract = True
        ordering = ('created_at',)


class Location(BaseBlogModel):
    name = models.CharField(
        max_length=settings.MAXLENGTH,
        verbose_name='Название места',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Category(BaseBlogModel):
    title = models.CharField(
        max_length=settings.MAXLENGTH,
        verbose_name='Заголовок',
    )
    description = models.TextField(
        verbose_name='Описание',
    )
    slug = models.SlugField(
        unique=True,
        help_text='Идентификатор страницы для URL; '
                  'разрешены символы латиницы, цифры, дефис и подчёркивание.',
        verbose_name='Идентификатор',
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Post(BaseBlogModel):
    title = models.CharField(
        max_length=settings.MAXLENGTH,
        verbose_name='Заголовок',
    )
    text = models.TextField(
        verbose_name='Текст',
    )
    image = models.ImageField(
        blank=True,
        upload_to='post_img',
        verbose_name='Фото',
    )
    pub_date = models.DateTimeField(
        help_text='Если установить дату и время в '
                  'будущем — можно делать отложенные публикации.',
        verbose_name='Дата и время публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Категория',
    )
    published = PublishedPostsManager()
    objects = models.Manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.author.get_username()},
        )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date', )


class Comment(BaseBlogModel):
    text = models.TextField(
        verbose_name='Комментарий',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор публикации',
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at', )
