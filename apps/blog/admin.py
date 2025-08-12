"""博客后台管理配置。

为 Category、Post、Comment 定制列表显示、搜索过滤与批量操作。
"""

from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.http import HttpRequest
from django.utils.html import format_html

from .models import Category, Comment, Post


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("name", "slug", "parent")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = (
        "title",
        "status",
        "published_at",
        "category",
        "author",
        "is_featured",
        "views",
        "preview_link",
    )
    list_filter = ("status", "category", "tags", "is_featured")
    search_fields = ("title", "slug", "body_markdown")
    list_editable = ("is_featured",)
    date_hierarchy = "published_at"
    autocomplete_fields = ("category",)
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ()
    readonly_fields = ("views", "reading_time")

    def preview_link(self, obj: Post) -> str:
        if obj.pk:
            return format_html('<a href="{}" target="_blank">预览</a>', obj.get_absolute_url())
        return "-"

    preview_link.short_description = "预览"


@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ("post", "user", "nickname", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("content", "nickname", "email")
    autocomplete_fields = ("post", "user", "parent")
    actions = ["approve_comments"]

    def approve_comments(self, request: HttpRequest, queryset: Any) -> None:
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"已通过 {updated} 条评论")

    approve_comments.short_description = "批量通过评论"
