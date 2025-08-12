"""博客视图。

提供文章列表、详情、分类/标签/归档/搜索列表页，以及评论提交视图。
包含中文 docstring 与类型注解，便于阅读与 IDE 推导。
"""

from __future__ import annotations

from typing import Any

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from taggit.models import Tag

from .forms import CommentForm
from .models import Category, Comment, Post


class PostListView(ListView):
    """文章列表页。

    支持分页、按发布时间倒序、置顶优先。
    """

    model = Post
    paginate_by = 10
    template_name = "blog/post_list.html"
    context_object_name = "posts"

    def get_queryset(self):  # type: ignore[override]
        return (
            Post.objects.published()
            .select_related("author", "category")
            .prefetch_related("tags")
            .featured_first()
        )


class PostDetailView(DetailView):
    """文章详情页，展示正文与评论。"""

    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:  # type: ignore[override]
        ctx = super().get_context_data(**kwargs)
        post: Post = ctx["post"]
        comments = (
            Comment.objects.filter(post=post, is_approved=True, parent__isnull=True)
            .select_related("user")
            .prefetch_related("replies")
        )
        ctx["comments"] = comments
        ctx["form"] = CommentForm(
            user=self.request.user if self.request.user.is_authenticated else None
        )
        # 若带有 reply_to 参数，尝试获取被回复的评论（仅允许回复已审核的顶级评论）
        reply_to_id = self.request.GET.get("reply_to")
        if reply_to_id and reply_to_id.isdigit():
            reply_to = Comment.objects.filter(
                id=int(reply_to_id), post=post, is_approved=True, parent__isnull=True
            ).first()
            if reply_to:
                ctx["reply_to"] = reply_to
        # 增加浏览量（简单实现，实际可用缓存去抖动）
        Post.objects.filter(pk=post.pk).update(views=post.views + 1)
        return ctx


def category_list(request: HttpRequest, slug: str) -> HttpResponse:
    """按分类查看文章列表。"""
    cat = get_object_or_404(Category, slug=slug)
    qs = (
        Post.objects.published()
        .filter(category=cat)
        .select_related("author", "category")
        .prefetch_related("tags")
    )
    paginator = Paginator(qs, 10)
    page = request.GET.get("page")
    posts = paginator.get_page(page)
    extra_qs = request.GET.copy()
    extra_qs.pop("page", None)
    querystring = f"&{extra_qs.urlencode()}" if extra_qs else ""
    return render(
        request,
        "blog/post_list.html",
        {"posts": posts, "category": cat, "querystring": querystring},
    )


def tag_list(request: HttpRequest, tag_slug: str) -> HttpResponse:
    """按标签查看文章列表。"""
    tag = get_object_or_404(Tag, slug=tag_slug)
    qs = (
        Post.objects.published()
        .filter(tags__in=[tag])
        .select_related("author", "category")
        .prefetch_related("tags")
    )
    paginator = Paginator(qs, 10)
    page = request.GET.get("page")
    posts = paginator.get_page(page)
    extra_qs = request.GET.copy()
    extra_qs.pop("page", None)
    querystring = f"&{extra_qs.urlencode()}" if extra_qs else ""
    return render(
        request, "blog/post_list.html", {"posts": posts, "tag": tag, "querystring": querystring}
    )


def archive_year(request: HttpRequest, year: int) -> HttpResponse:
    """按年份归档。"""
    start = timezone.datetime(year, 1, 1, tzinfo=timezone.get_current_timezone())
    end = timezone.datetime(year + 1, 1, 1, tzinfo=timezone.get_current_timezone())
    qs = Post.objects.published().filter(published_at__gte=start, published_at__lt=end)
    paginator = Paginator(qs, 10)
    page = request.GET.get("page")
    posts = paginator.get_page(page)
    extra_qs = request.GET.copy()
    extra_qs.pop("page", None)
    querystring = f"&{extra_qs.urlencode()}" if extra_qs else ""
    return render(
        request,
        "blog/post_list.html",
        {"posts": posts, "archive_year": year, "querystring": querystring},
    )


def search(request: HttpRequest) -> HttpResponse:
    """全文搜索（简单版，基于 title/body_markdown LIKE）。"""
    q = request.GET.get("q", "").strip()
    qs = Post.objects.published()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(body_markdown__icontains=q))
    paginator = Paginator(qs, 10)
    page = request.GET.get("page")
    posts = paginator.get_page(page)
    extra_qs = request.GET.copy()
    extra_qs.pop("page", None)
    querystring = f"&{extra_qs.urlencode()}" if extra_qs else ""
    return render(
        request, "blog/post_list.html", {"posts": posts, "q": q, "querystring": querystring}
    )


@require_POST
def submit_comment(request: HttpRequest, slug: str) -> HttpResponse:
    """提交评论。

    - 已登录用户：可不填昵称和邮箱；
    - 未登录用户：必须填写昵称、邮箱；
    - 评论默认进入待审核状态，后台通过后显示。
    """
    post = get_object_or_404(Post, slug=slug)
    form = CommentForm(request.POST, user=request.user if request.user.is_authenticated else None)
    if form.is_valid():
        comment: Comment = form.save(commit=False)
        comment.post = post
        if request.user.is_authenticated:
            comment.user = request.user
        # 仅允许回复“已审核的顶级评论”，保持两级结构
        parent_id = request.POST.get("parent_id")
        if parent_id and parent_id.isdigit():
            parent = Comment.objects.filter(
                id=int(parent_id), post=post, is_approved=True, parent__isnull=True
            ).first()
            if parent:
                comment.parent = parent
        comment.is_approved = False
        comment.save()
        messages.success(request, _("评论已提交，待审核后显示。"))
        return HttpResponseRedirect(f"{post.get_absolute_url()}#comment-form")
    messages.error(request, _("评论提交失败，请检查表单信息。"))
    return HttpResponseRedirect(f"{post.get_absolute_url()}#comment-form")
