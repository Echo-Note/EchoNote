"""博客应用 URL 路由配置。

包含首页文章列表、详情、分类、标签、归档、搜索与评论提交等路由。
"""

from __future__ import annotations

from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("post/<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
    path("category/<slug:slug>/", views.category_list, name="category"),
    path("tag/<slug:tag_slug>/", views.tag_list, name="tag"),
    path("archive/<int:year>/", views.archive_year, name="archive_year"),
    path("search/", views.search, name="search"),
    path("post/<slug:slug>/comment/", views.submit_comment, name="submit_comment"),
]
