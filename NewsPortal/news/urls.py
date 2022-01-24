from django.urls import path
from .views import NewsList, NewsDetail, NewsSearch, NewsCreateView, NewsUpdateView, NewsDeleteView, CategoryView, subscribe_category
urlpatterns = [
    path('', NewsList.as_view()),
    path('search', NewsSearch.as_view()),
    path('add', NewsCreateView.as_view(), name='news_create'),
    path('<int:pk>', NewsDetail.as_view(), name='news_detail'),
    path('<int:pk>/edit', NewsUpdateView.as_view(), name='news_edit'),
    path('<int:pk>/delete', NewsDeleteView.as_view(), name='news_delete'),
    path('category/<int:cats>/', CategoryView, name='post-category'),
    path('category/<int:cats>/subscribe_category', subscribe_category, name='subscribe-category')
    ]
