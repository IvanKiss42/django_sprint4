from django.shortcuts import get_object_or_404, render, redirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Category, Post, Comment
from .forms import PostForm, UserForm, CommentForm
from .functions import Paginator_10


POSTS_PER_PAGE = 10


@login_required
def create_post(request):
    template = 'blog/create.html'
    form = PostForm(
        request.POST or None, files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('blog:profile', request.user)
    return render(request, template, context)


def profile(request, slug):
    template = 'blog/profile.html'
    profile = get_object_or_404(User, username=slug)
    if request.user.username != slug:
        posts = Post.common_filtration().filter(
            author=profile).order_by('-pub_date')
    else:
        posts = Post.objects.filter(
            author=profile).annotate(
            comment_count=Count('comment')).order_by('-pub_date')
    page_obj = Paginator_10(request, posts, POSTS_PER_PAGE)
    context = {'profile': profile,
               'page_obj': page_obj}
    return render(request, template, context)


def edit_profile(request):
    template = 'blog/user.html'
    instance = get_object_or_404(User, username=request.user)
    form = UserForm(request.POST or None, instance=instance)
    context = {'form': form}
    if form.is_valid():
        send_mail(
            subject='Profile changes',
            message=f'{request.user} изменил свои данные',
            from_email='blogicum@ya_prac.ru',
            recipient_list=['admin_user@ya_prac.ru'],
            fail_silently=True,
        )
        form.save()
        return redirect('blog:profile', slug=request.user.username)
    return render(request, template, context)


def post_detail(request, pk):
    template = 'blog/detail.html'
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        post = get_object_or_404(Post.common_filtration(), pk=pk)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post=pk)
    context = {'post': post,
               'form': form,
               'comments': comments}
    return render(request, template, context)


"""
Тут мне в какой-то момент было удобней использовать DetailView
Но позже не разобрался как навесить в него условий на проверку пользователя
без миксинов, поэтому вернулся к обычным views
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comment.select_related('author')
        return context
"""


def index(request):
    template = 'blog/index.html'
    posts = Post.common_filtration(
    ).order_by('-pub_date')
    page_obj = Paginator_10(request, posts, POSTS_PER_PAGE)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug)
    posts = Post.common_filtration().filter(
        category__slug=category_slug
    ).order_by('-pub_date')
    page_obj = Paginator_10(request, posts, POSTS_PER_PAGE)
    context = {'category': category,
               'page_obj': page_obj}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=post_id)


def edit_post(request, post_id):
    template = 'blog/create.html'
    instance = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=instance)
    context = {'form': form}
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        if (not request.user.is_authenticated
                or request.user != instance.author):
            return redirect('blog:post_detail', pk=post_id)
        post.author = request.user
        post.post = instance
        post.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, template, context)


def delete_post(request, post_id):
    template = 'blog/create.html'
    instance = get_object_or_404(Post, pk=post_id)
    form = PostForm(instance=instance)
    context = {'form': form}
    if request.method == 'POST':
        if (not request.user.is_authenticated
                or request.user != instance.author):
            return redirect('blog:post_detail', pk=post_id)
        instance.delete()
        return redirect('blog:index')
    return render(request, template, context)


@login_required
def edit_comment(request, post_id, comment_id):
    template = 'blog/comment.html'
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author == request.user:
        form = CommentForm(request.POST or None, instance=comment)
        context = {'form': form,
                   'comment': comment}
    else:
        raise PermissionDenied
    if request.method == 'POST' and form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = Post.objects.get(pk=post_id)
        comment.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, template, context)


@login_required
def delete_comment(request, post_id, comment_id):
    template = 'blog/comment.html'
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.author == request.user:
        context = {'comment': comment}
    else:
        raise PermissionDenied
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, template, context)
