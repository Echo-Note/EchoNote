"""博客核心数据模型定义。

包含分类（Category）、文章（Post）与评论（Comment）。

设计要点：
- Post 支持 Markdown 到 HTML 的渲染、阅读时长估算、发布时间与发布状态；
- 使用 django-taggit 管理标签；
- Category 支持层级（可选父分类）；
- Comment 支持二级回复与审核流；
- 所有模型包含详细中文注释与类型注解。
"""

import markdown as md
from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager

from apps.common.models import SEOMixin, SluggedModel, TimeStampedModel


class Category(TimeStampedModel, SluggedModel):
    """文章分类模型，支持可选父级构成树形结构。"""

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("分类名称"),
        db_comment="分类名称（唯一）",
    )
    description = models.TextField(blank=True, verbose_name=_("描述"), db_comment="分类描述")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("父级"),
        db_comment="父级分类（可为空）",
    )

    class Meta:
        verbose_name = _("分类")
        verbose_name_plural = _("分类")
        ordering = ["name"]
        db_table_comment = "文章分类"

    def __str__(self) -> str:
        return self.name

    def get_slug_source(self) -> str:
        return self.name


class PostQuerySet(models.QuerySet["Post"]):
    """Post 的自定义查询集。"""

    def published(self) -> QuerySet:
        """
        筛选已发布的文章。

        仅包含状态为 PUBLISHED 且发布时间不晚于当前时间的文章。
        """
        return self.filter(status=Post.Status.PUBLISHED, published_at__lte=timezone.now())

    def featured_first(self) -> QuerySet:
        """
        优先展示置顶文章，按发布时间倒序排列。

        :return: 排序后的查询集
        """
        return self.order_by(models.F("is_featured").desc(nulls_last=True), "-published_at", "-id")


class Post(TimeStampedModel, SEOMixin, SluggedModel):
    """文章模型，包含 Markdown 正文与派生 HTML、标签、分类、发布状态等。"""

    class Status(models.TextChoices):
        DRAFT = "draft", _("草稿")
        SCHEDULED = "scheduled", _("计划发布")
        PUBLISHED = "published", _("已发布")

    title = models.CharField(max_length=200, verbose_name=_("标题"), db_comment="文章标题")
    excerpt = models.TextField(blank=True, verbose_name=_("摘要"), db_comment="文章摘要")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("作者"),
        db_comment="作者",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("分类"),
        db_comment="所属分类（可为空）",
    )
    tags = TaggableManager(blank=True, verbose_name=_("标签"))

    body_markdown = models.TextField(verbose_name=_("正文 Markdown"), db_comment="Markdown 正文")
    body_html = models.TextField(
        blank=True, verbose_name=_("正文 HTML"), db_comment="渲染后的 HTML 正文"
    )

    cover_image = models.ImageField(
        upload_to="covers/",
        null=True,
        blank=True,
        verbose_name=_("封面图"),
        db_comment="封面图片",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_("状态"),
        db_comment="发布状态",
    )
    published_at = models.DateTimeField(
        null=True, blank=True, verbose_name=_("发布时间"), db_comment="发布时间"
    )

    is_featured = models.BooleanField(
        default=False, verbose_name=_("置顶/推荐"), db_comment="是否置顶/推荐"
    )
    views = models.PositiveIntegerField(default=0, verbose_name=_("浏览量"), db_comment="浏览次数")
    reading_time = models.PositiveIntegerField(
        default=1, verbose_name=_("阅读时长(分钟)"), db_comment="预计阅读时长（分钟）"
    )
    allow_comment = models.BooleanField(
        default=True, verbose_name=_("允许评论"), db_comment="是否允许评论"
    )

    objects = PostQuerySet.as_manager()

    class Meta:
        verbose_name = _("文章")
        verbose_name_plural = _("文章")
        ordering = ["-published_at", "-id"]
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["slug"]),
        ]
        db_table_comment = "文章"

    def __str__(self) -> str:
        return self.title

    def get_slug_source(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        """
        获取文章的绝对 URL。

        用于在模板中生成文章详情页链接，以及 Django Admin 中的“查看站点”按钮。

        :return: 文章详情页的完整 URL 路径
        """
        return reverse("blog:post_detail", kwargs={"slug": self.slug})

    @staticmethod
    def render_markdown(text: str) -> str:
        """
        将 Markdown 文本渲染为 HTML。

        使用 markdown 库并启用以下扩展：
        - extra: 包含常用语法如表格、定义列表等；
        - codehilite: 代码高亮；
        - toc: 生成目录；
        - sane_lists: 更合理的列表解析；
        - smarty: 智能引号替换。

        :param text: 原始 Markdown 文本
        :return: 渲染后的 HTML 字符串
        """
        return md.markdown(
            text or "",
            extensions=["extra", "codehilite", "toc", "sane_lists", "smarty"],
            output_format="html",
        )

    @staticmethod
    def estimate_reading_time(text: str) -> int:
        """
        估算阅读时长（分钟）。

        :param text: 输入文本
        :return: 阅读时长（分钟）
        """
        words = len((text or "").split())
        minutes = max(1, int(round(words / 200.0)))
        return minutes

    def save(self, *args, **kwargs):
        # auto set published_at
        if self.status == Post.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        # render markdown
        self.body_html = self.render_markdown(self.body_markdown)
        # reading time
        self.reading_time = self.estimate_reading_time(self.body_markdown)
        super().save(*args, **kwargs)


class Comment(TimeStampedModel):
    """文章评论模型，支持二级回复与审核。"""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("文章"),
        db_comment="所属文章",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("用户"),
        db_comment="评论用户（可为空）",
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("父评论"),
        db_comment="父评论（可为空）",
    )

    nickname = models.CharField(
        max_length=50, blank=True, verbose_name=_("昵称"), db_comment="访客昵称"
    )
    email = models.EmailField(blank=True, verbose_name=_("邮箱"), db_comment="访客邮箱")

    content = models.TextField(verbose_name=_("内容"), db_comment="评论内容")
    is_approved = models.BooleanField(
        default=False, verbose_name=_("已审核"), db_comment="是否已审核"
    )
    ip = models.GenericIPAddressField(
        null=True, blank=True, verbose_name=_("IP"), db_comment="评论 IP 地址"
    )
    ua = models.CharField(
        max_length=255, blank=True, verbose_name=_("UA"), db_comment="用户代理 UA"
    )

    class Meta:
        verbose_name = _("评论")
        verbose_name_plural = _("评论")
        ordering = ["created_at"]
        db_table_comment = "文章评论"

    def __str__(self) -> str:
        return f"Comment({self.pk}) on {self.post}"
