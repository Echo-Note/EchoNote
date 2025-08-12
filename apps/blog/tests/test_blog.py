from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.blog.models import Category, Comment, Post


class BlogBasicTests(TestCase):
    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(username="author", password="pass1234")
        self.cat = Category.objects.create(name="Django")
        self.post = Post.objects.create(
            title="Hello World",
            author=self.user,
            category=self.cat,
            body_markdown="# Title\n\nSome content with `code`.",
            status=Post.Status.PUBLISHED,
            published_at=timezone.now(),
        )

    def test_post_markdown_render_and_reading_time(self) -> None:
        self.post.refresh_from_db()
        self.assertIn("<h1", self.post.body_html)
        self.assertGreaterEqual(self.post.reading_time, 1)

    def test_post_get_absolute_url(self) -> None:
        url = self.post.get_absolute_url()
        self.assertTrue(url)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_list_and_search_views(self) -> None:
        # list
        resp = self.client.get(reverse("blog:post_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.post.title)
        # search
        resp = self.client.get(reverse("blog:search"), {"q": "Hello"})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.post.title)

    def test_category_and_tag_and_archive(self) -> None:
        # category
        resp = self.client.get(reverse("blog:category", kwargs={"slug": self.cat.slug}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.post.title)
        # archive
        year = self.post.published_at.year
        resp = self.client.get(reverse("blog:archive_year", kwargs={"year": year}))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, self.post.title)

    def test_submit_comment_requires_moderation(self) -> None:
        url = reverse("blog:submit_comment", kwargs={"slug": self.post.slug})
        data = {"content": "Nice post!", "nickname": "Guest", "email": "guest@example.com"}
        resp = self.client.post(url, data, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            Comment.objects.filter(post=self.post, content="Nice post!", is_approved=False).exists()
        )

    def test_sitemap_and_robots(self) -> None:
        # sitemap should include post url
        resp = self.client.get("/sitemap.xml")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(self.post.get_absolute_url(), resp.content.decode())
        # robots.txt
        resp = self.client.get("/robots.txt")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Sitemap:", resp.content.decode())
