
from django.test import TestCase
from django.urls import reverse

from .models import Category, Resource


class PageViewsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(
            name="Programming",
            description="Programming topics"
        )

        cls.resource = Resource.objects.create(
            title="Python basics",
            description="Variables and functions",
            available=True,
            category=cls.category
        )

        Resource.objects.create(
            title="Django models",
            description="Database fundamentals",
            available=False,
            category=cls.category
        )

    def test_home_page_renders(self):
        response = self.client.get(
            reverse("pages:home")
        )

        self.assertEqual(response.status_code, 200)

    def test_resources_page_shows_example_data(self):
        response = self.client.get(
            reverse("pages:resources")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python basics")
        self.assertContains(response, "Django models")
        self.assertContains(response, "Available")
        self.assertContains(response, "Coming soon")

    def test_about_page_renders(self):
        response = self.client.get(
            reverse("pages:about")
        )

        self.assertEqual(response.status_code, 200)

    def test_resources_show_category(self):
        response = self.client.get(
            reverse("pages:resources")
        )

        self.assertContains(response, "Programming")

    def test_resource_is_saved_in_database(self):
        resource = Resource.objects.get(
            title="Python basics"
        )

        self.assertEqual(
            resource.category.name,
            "Programming"
        )
