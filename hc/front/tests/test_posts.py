from django.urls import reverse

from hc.test import BaseTestCase
from hc.front.models import Post


class PostsTestCase(BaseTestCase):
    def setUp(self):
        super(PostsTestCase, self).setUp()

    def test_user_can_view_all_blog_posts(self):
        post = Post(user=self.alice, title="Post Title", body="Post Body", publish=True)
        post.save()

        response = self.client.get(reverse("hc-post"))
        self.assertContains(response, "Post Title", status_code=200)

    def test_user_see_no_post_messages_if_there_are_no_posts_to_display(self):
        response = self.client.get(reverse("hc-post"))
        self.assertContains(response, "No posts at this time", status_code=200)

    def test_authenticated_user_can_view_post_creation_page(self):
        self.client.login(username="alice@example.org", password="password")
        response = self.client.get(reverse("hc-add-post"))

        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_create_blog(self):
        self.client.login(username="alice@example.org", password="password")
        payload = {
            "title": "Post Title",
            "body": "Post body"
        }

        response = self.client.post(reverse("hc-add-post"), data=payload)

        post = Post.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Post.objects.count(), 1)
        self.assertListEqual([post.title, post.body], [payload.get("title"), payload.get("body")])

    def test_view_all_posts_shows_all_posts(self):
        response = self.client.get(reverse("hc-all-posts"))

        self.assertEqual(response.status_code, 200)

    def test_edit_updates_post(self):
        self.client.login(username="alice@example.org", password="password")
        post = Post(title="Post Title", body="Post body", user=self.alice)
        post.save()
        payload = {
            "title": "Updated Post Title",
            "body": "Updated post body"
        }
        response = self.client.post("/post/{}/edit/".format(post.slug), data=payload)
        post = Post.objects.first()

        self.assertEqual(response.status_code, 302)
        self.assertListEqual([post.title, post.body], [payload.get("title"), payload.get("body")])

    def test_delete_removes_a_post(self):
        self.client.login(username="alice@example.org", password="password")
        post = Post(title="Post Title", body="Post body", user=self.alice)
        post.save()

        self.assertEqual(Post.objects.count(), 1)

        response = self.client.delete("/post/{}/delete/".format(post.slug))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/posts/")
        self.assertEqual(Post.objects.count(), 0)

    def test_delete_fails_gracefully_when_post_doesnt_exist(self):
        response = self.client.delete("/post/non-existent-post/delete/")

        self.assertEqual(response.status_code, 302)
