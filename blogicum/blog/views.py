from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.db.models import Count
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView
)
from django.urls import reverse, reverse_lazy
from django.core.paginator import Paginator
from blog.models import Post, Category, Comment, User
from blog.forms import BlogForm, CommentForm, ProfileForm


class OnlyAuthorMixin(UserPassesTestMixin):
    """Миксин для проверки авторизации."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostsReverseMixin:
    """Миксин для постов."""

    model = Post
    form_class = BlogForm
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class PostCreateView(LoginRequiredMixin, PostsReverseMixin, CreateView):
    """Создание поста."""

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(OnlyAuthorMixin, PostsReverseMixin, UpdateView):
    """Редактирование поста"""

    pass


class PostDeleteView(OnlyAuthorMixin, PostsReverseMixin, DeleteView):
    """Удаление поста."""

    pass


class ProfileListView(ListView):
    """Возвращает посты автора"""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = settings.PAGINATED_BY

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        queryset = self.author.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(OnlyAuthorMixin, UpdateView):
    """Изменение профиля."""

    model = Post
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Добавление комментария."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        form.instance.author = self.request.user
        form.save()
        return redirect('blog:post_detail', post_id=self.kwargs['pk'])


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование комментария"""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = "comment_pk"

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

    def get_success_url(self):
        post_id = self.object.post.pk
        return reverse('blog:post_detail', kwargs={'post_id': post_id})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление комментария"""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = "comment_id"

    def get_queryset(self):
        return Comment.objects.filter(author=self.request.user)

    def get_success_url(self):
        post_id = self.object.post.pk
        return reverse('blog:post_detail', kwargs={'post_id': post_id})


def index(request):
    """Функция возвращает главную страницу."""
    posts = (
        Post.published
        .select_related(
            'location',
            'category',
            'author'
        )
        .order_by('-pub_date')
        .annotate(comment_count=Count('comments'))
    )
    paginator = Paginator(posts, settings.PAGINATED_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'blog/index.html', context)


def post_detail(request, post_id):
    """Функция возвращает пост."""
    post = (
        get_object_or_404(
            (Post.published
             .select_related(
                 'location',
                 'category',
                 'author',)
             ), pk=post_id
        )
    )
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    """Функция возвращает категорию поста."""
    category = (
        get_object_or_404(
            Category,
            slug=category_slug,
            is_published=True
        )
    )
    posts = category.posts.filter(
        is_published=True,
        pub_date__lte=timezone.now()
    )
    paginator = Paginator(posts, settings.PAGINATED_BY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)
