from django_filters import FilterSet, CharFilter, DateFilter
from .models import Post


class PostFilter(FilterSet):
    title_filter = CharFilter(field_name='post_title', lookup_expr='icontains', label='По названию')
    author_filter = CharFilter(field_name='post_author__author_id__username', lookup_expr='icontains', label='По автору')
    time_filter = DateFilter(field_name='post_time', lookup_expr='gt', label='Позднее даты (yyyy-mm-dd)')

    class Meta:
        model = Post
        fields = ('title_filter', 'author_filter', 'time_filter')
