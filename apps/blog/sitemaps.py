"""Sitemaps for the blog app.

提供文章(Post)的站点地图，便于搜索引擎抓取。
"""

from __future__ import annotations

from django.contrib.sitemaps import Sitemap

from .models import Post


class PostSitemap(Sitemap):
    """
    文章站点地图
    """

    changefreq = "weekly"  # 每周更新
    priority = 0.6  # 优先级

    def items(self):
        """
        返回所有已发布的文章对象列表

        :return: QuerySet of Post objects
        """
        return Post.objects.published()

    def lastmod(self, obj: Post):
        """
        返回文章的最后修改时间

        :param obj: Post 对象
        :return: 最后修改时间
        """
        return obj.updated_at or obj.published_at

    def location(self, obj: Post):
        """
        返回文章的绝对 URL 路径

        :param obj: Post 对象
        :return: 文章详情页的 URL 路径
        """
        return obj.get_absolute_url()
