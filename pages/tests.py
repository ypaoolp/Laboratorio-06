from django.test import SimpleTestCase
from django.urls import reverse


class PageViewsTests(SimpleTestCase):
    def test_home_page_renders(self):
        """RF01: GET / muestra encabezado y bienvenida."""
        response = self.client.get(reverse("pages:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/home.html")
        self.assertContains(response, "Welcome")
        self.assertContains(response, "ClassroomHub")

    def test_resources_page_shows_example_data(self):
        """RF02 y RF06: GET /resources/ muestra la lista de recursos y distingue disponibilidad."""
        response = self.client.get(reverse("pages:resources"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/resources.html")
        self.assertContains(response, "Python basics")
        self.assertContains(response, "Available")
        self.assertContains(response, "Coming soon")

    def test_about_page_renders(self):
        """RF03: GET /about/ muestra el propósito del proyecto."""
        response = self.client.get(reverse("pages:about"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/about.html")
        self.assertContains(response, "Practice URL routing, views, and templates.")

    def test_home_navigation_links_to_resources(self):
        """RF04 y RF05: Navegar entre páginas y reutilizar el diseño de base.html."""
        response = self.client.get(reverse("pages:home"))

        self.assertTemplateUsed(response, "pages/base.html")
        self.assertContains(response, f'href="{reverse("pages:home")}"')
        self.assertContains(response, f'href="{reverse("pages:resources")}"')
        self.assertContains(response, f'href="{reverse("pages:about")}"')

    def test_unknown_page_returns_not_found(self):
        """RF07: Una dirección desconocida produce 404."""
        response = self.client.get("/not-found/")

        self.assertEqual(response.status_code, 404)
