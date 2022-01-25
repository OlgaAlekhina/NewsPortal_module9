from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Post, Category, Author
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required


class NewsList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    ordering = ['-post_time']
    paginate_by = 10


class NewsDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class NewsSearch(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'news'
    ordering = ['-post_time']
    paginate_by = 5
    queryset = Post.objects.order_by("pk")

    def get_filter(self):
        return PostFilter(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):
        qs = self.get_filter().qs
        return qs

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        filter = self.get_filter()
        context['filter'] = filter

        filter_params = ""
        for f_name in [str(k) for k in filter.filters]:
            if f_name in filter.data:
                filter_params += f"&{f_name}={filter.data[f_name]}"
        context['filter_params'] = filter_params

        context['get_dict'] = {
            k: value[0] for k, value in dict(self.request.GET.copy()).items() if k != 'page'
         }
        return context


class NewsCreateView(PermissionRequiredMixin, CreateView):
    template_name = 'post_create_form.html'
    form_class = PostForm
    permission_required = ('news.add_post')


class NewsUpdateView(PermissionRequiredMixin, UpdateView):
    template_name = 'post_update_form.html'
    form_class = PostForm
    permission_required = ('news.change_post')

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class NewsDeleteView(PermissionRequiredMixin, DeleteView):
    template_name = 'post_delete_form.html'
    queryset = Post.objects.all()
    success_url = '/news/'
    permission_required = ('news.delete_post')


class UserPageView(LoginRequiredMixin, TemplateView):
    template_name = 'user_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class CategoryListView(ListView):
    context_object_name = 'category_posts'
    template_name = 'post_category.html'
    paginate_by = 5

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['cats'])
        return Post.objects.filter(categories=self.category).order_by('-post_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['is_not_subscriber'] = not self.request.user.subscribed_categories.filter(id=self.kwargs['cats']).exists()
        return context


@login_required
def upgrade_me(request):
    user = request.user
    authors_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        authors_group.user_set.add(user)
        Author.objects.create(author=user)
    return redirect('/user_page')


@login_required
def subscribe_category(request, cats):
    user = request.user
    current_cat = Category.objects.get(id=cats)
    current_cat.subscribers.add(user)
    return redirect(current_cat)
