"""通用抽象模型与混入。

提供以下功能：
- TimeStampedModel：自动创建/更新时间字段；
- SoftDeleteModel：软删除标记与时间；
- SEOMixin：SEO 元信息字段；
- SluggedModel：基于对象属性自动生成唯一 slug，便于友好链接。

所有模型均包含中文注释与类型标注，方便 IDE 类型推导与阅读。
"""

from __future__ import annotations

from typing import Any

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """抽象时间戳模型：提供创建时间与更新时间。

    注意：Django 会在保存记录时自动维护该字段的时间。
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("创建时间"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("更新时间"))
    version = models.PositiveSmallIntegerField(default=1, verbose_name=_("版本"))

    class Meta:
        abstract = True

    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        保存记录时自动增加版本号。

        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: None
        """
        self.version += 1
        super().save(*args, **kwargs)


class SoftDeleteModel(models.Model):
    """抽象软删除模型：通过布尔标记与删除时间实现逻辑删除。"""

    is_deleted = models.BooleanField(default=False, verbose_name=_("已删除"))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_("删除时间"))

    class Meta:
        abstract = True

    def delete(self, *args: Any, **kwargs: Any) -> None:
        """执行软删除操作，标记对象为已删除并记录删除时间。

        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: None
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


class SEOMixin(models.Model):
    """SEO 元信息混入：为页面/文章等提供标题与描述。"""

    meta_title = models.CharField(max_length=255, blank=True, verbose_name=_("SEO 标题"))
    meta_description = models.CharField(max_length=500, blank=True, verbose_name=_("SEO 描述"))

    class Meta:
        abstract = True


class SluggedModel(models.Model):
    """提供唯一 slug 字段，并在保存时自动生成。

    子类可通过覆写 get_slug_source 指定 slug 的来源（默认取 title 字段）。
    """

    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("Slug"))

    class Meta:
        abstract = True

    def get_slug_source(self) -> str:
        """返回用于生成 slug 的源字符串，默认使用 title 属性。"""
        return getattr(self, "title", "")

    def generate_unique_slug(self) -> str:
        """根据源字符串生成唯一的 slug。

        当生成的 slug 已存在时，会在末尾追加递增序号以保证唯一。
        """
        base = slugify(self.get_slug_source())[:50] or "item"
        candidate = base
        Model = self.__class__
        idx = 1
        while Model.objects.filter(slug=candidate).exclude(pk=self.pk).exists():  # type: ignore[attr-defined]
            candidate = f"{base}-{idx}"
            idx += 1
        return candidate

    def save(self, *args: Any, **kwargs: Any) -> None:  # type: ignore[override] # noqa: DJ012
        """在首次保存时自动填充 slug。"""
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
