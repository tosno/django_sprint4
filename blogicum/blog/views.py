from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView
)
from django.urls import reverse
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit_post'] = '/edit/' in self.request.path
        context['is_delete_post'] = '/delete/' in self.request.path
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class CommentPostMixin:
    """Миксин для комментариев."""

    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        return self.request.user.comments.filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit_comment'] = '/edit_comment/' in self.request.path
        return context

    def get_success_url(self):
        post_id = self.object.post.pk
        return reverse('blog:post_detail', kwargs={'pk': post_id})


class PostCreateView(LoginRequiredMixin, PostsReverseMixin, CreateView):
    """Создание поста."""

    pass


class PostUpdateView(LoginRequiredMixin, PostsReverseMixin, UpdateView):
    """Редактирование поста"""

    def dispatch(self, request, *args, **kwargs):
        instance = self.get_object()
        post_id = self.kwargs.get('pk')
        if instance.author != request.user:
            return redirect(
                'blog:post_detail',
                pk=post_id,
            )
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(OnlyAuthorMixin, PostsReverseMixin, DeleteView):
    """Удаление поста."""

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BlogForm(instance=self.get_object())
        return context


class ProfileListView(ListView):
    """Возвращает посты автора"""

    model = Post
    template_name = 'blog/profile.html'
    paginate_by = settings.PAGINATED_BY

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        queryset = (
            self.author
            .posts.order_by('-pub_date')
            .annotate(comment_count=Count('comments'))
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Изменение профиля."""

    model = Post
    form_class = ProfileForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.request.user.username)

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
        return redirect('blog:post_detail', pk=self.kwargs['pk'])


class CommentUpdateView(LoginRequiredMixin, CommentPostMixin, UpdateView):
    """Редактирование комментария"""

    pass


class CommentDeleteView(LoginRequiredMixin, CommentPostMixin, DeleteView):
    """Удаление комментария"""

    pass


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


def post_detail(request, pk):
    """Функция возвращает пост."""
    post = (
        get_object_or_404(
            (Post.objects
             .select_related(
                 'location',
                 'category',
                 'author',)
             ), pk=pk
        )
    )
    if request.user != post.author and (
        post.is_published is False
        or post.category.is_published is False
        or post.pub_date > timezone.now()
    ):
        raise Http404
    else:
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
