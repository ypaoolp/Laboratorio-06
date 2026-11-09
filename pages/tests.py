from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import ProtectedError
from django.test import Client, TestCase
from django.urls import reverse

from .forms import ResourceForm
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

    def test_home_navigation_links_to_resources(self):
        response = self.client.get(reverse("pages:home"))

        self.assertTemplateUsed(response, "pages/base.html")
        self.assertContains(response, f'href="{reverse("pages:home")}"')
        self.assertContains(response, f'href="{reverse("pages:resources")}"')
        self.assertContains(response, f'href="{reverse("pages:about")}"')

    def test_unknown_page_returns_not_found(self):
        response = self.client.get("/not-found/")

        self.assertEqual(response.status_code, 404)

    def test_category_str(self):
        self.assertEqual(str(self.category), "Programming")

    def test_resource_str(self):
        self.assertEqual(str(self.resource), "Python basics")

    def test_category_cannot_be_deleted_with_resources(self):
        with self.assertRaises(ProtectedError):
            self.category.delete()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.password = "ExampleTestPassword!2026"
        self.user = get_user_model().objects.create_user(
            username="reader",
            password=self.password,
        )

    def test_signup_page_renders(self):
        response = self.client.get(reverse("pages:signup"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/signup.html")

    def test_signup_creates_regular_user(self):
        response = self.client.post(
            reverse("pages:signup"),
            {
                "username": "new_reader",
                "password1": "NewExamplePassword!2026",
                "password2": "NewExamplePassword!2026",
            },
        )

        self.assertRedirects(response, reverse("pages:login"))
        account = get_user_model().objects.get(username="new_reader")
        self.assertFalse(account.is_staff)
        self.assertFalse(account.is_superuser)
        self.assertTrue(account.check_password("NewExamplePassword!2026"))

    def test_signup_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("pages:signup"),
            {
                "username": "invalid_reader",
                "password1": "ExamplePassword!2026",
                "password2": "DifferentPassword!2026",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            get_user_model().objects.filter(
                username="invalid_reader"
            ).exists()
        )

    def test_signup_rejects_existing_username(self):
        response = self.client.post(
            reverse("pages:signup"),
            {
                "username": "reader",
                "password1": "ExamplePassword!2026",
                "password2": "ExamplePassword!2026",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            get_user_model().objects.filter(username="reader").count(),
            1,
        )

    def test_login_rejects_wrong_password(self):
        response = self.client.post(
            reverse("pages:login"),
            {"username": "reader", "password": "wrong"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("pages:login"),
            {"username": "reader", "password": self.password},
        )

        self.assertRedirects(response, reverse("pages:dashboard"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_respects_safe_next(self):
        destination = reverse("pages:dashboard")
        response = self.client.post(
            reverse("pages:login") + f"?next={destination}",
            {
                "username": "reader",
                "password": self.password,
                "next": destination,
            },
        )

        self.assertRedirects(response, destination)

    def test_anonymous_dashboard_redirects_to_login(self):
        response = self.client.get(reverse("pages:dashboard"))

        self.assertRedirects(
            response,
            reverse("pages:login") + "?next=/dashboard/",
        )

    def test_dashboard_session_counter_increments(self):
        self.client.force_login(self.user)

        first = self.client.get(reverse("pages:dashboard"))
        second = self.client.get(reverse("pages:dashboard"))

        self.assertEqual(first.context["visit_count"], 1)
        self.assertEqual(second.context["visit_count"], 2)

    def test_logout_get_is_not_allowed(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("pages:logout"))

        self.assertEqual(response.status_code, 405)
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_post_ends_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("pages:logout"))

        self.assertRedirects(response, reverse("pages:home"))
        self.assertNotIn("_auth_user_id", self.client.session)
        protected = self.client.get(reverse("pages:dashboard"))
        self.assertEqual(protected.status_code, 302)

    def test_login_post_without_csrf_is_rejected(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.get(reverse("pages:login"))

        response = csrf_client.post(
            reverse("pages:login"),
            {"username": "reader", "password": self.password},
        )

        self.assertEqual(response.status_code, 403)


class ResourceReviewPermissionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="review_candidate",
            password="ExampleTestPassword!2026",
        )
        category = Category.objects.create(name="Programming")
        Resource.objects.create(
            title="Python basics",
            category=category,
        )

        content_type = ContentType.objects.get_for_model(Resource)
        permission = Permission.objects.get(
            content_type=content_type,
            codename="view_resource",
        )

        self.reviewers = Group.objects.create(
            name="Catalog reviewers",
        )
        self.reviewers.permissions.add(permission)

    def test_anonymous_review_redirects_to_login(self):
        response = self.client.get(reverse("pages:resource-review"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("pages:login"), response.url)

    def test_regular_user_cannot_open_review(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("pages:resource-review"))

        self.assertEqual(response.status_code, 403)

    def test_reviewer_can_open_review(self):
        self.user.groups.add(self.reviewers)
        self.client.force_login(self.user)

        response = self.client.get(reverse("pages:resource-review"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python basics")
        self.assertTemplateUsed(response, "pages/review.html")

    def test_reviewer_does_not_become_staff(self):
        self.user.groups.add(self.reviewers)
        self.user.refresh_from_db()

        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)

    def test_public_catalog_remains_available(self):
        response = self.client.get(reverse("pages:resources"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Python basics")

    def test_typing_review_url_cannot_bypass_permission(self):
        self.client.force_login(self.user)

        response = self.client.get("/resources/review/")

        self.assertEqual(response.status_code, 403)


# =============================================================================
# Laboratorio 09 — CRUD, Forms, CBV, Permisos de Editor (27 pruebas nuevas)
# =============================================================================


class ResourceFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Web Development")

    def test_valid_form_data(self):
        data = {
            "title": "Django Deep Dive",
            "description": "Comprehensive guide to Django",
            "resource_type": "Book",
            "category": self.category.pk,
            "available": True,
        }
        form = ResourceForm(data=data)
        self.assertTrue(form.is_valid())

    def test_title_normalized_and_stripped(self):
        data = {
            "title": "   FastAPI Guide   ",
            "description": "API building",
            "resource_type": "Course",
            "category": self.category.pk,
            "available": True,
        }
        form = ResourceForm(data=data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["title"], "FastAPI Guide")

    def test_title_too_short_fails_validation(self):
        data = {
            "title": "Go",
            "description": "Golang basics",
            "resource_type": "Tutorial",
            "category": self.category.pk,
            "available": True,
        }
        form = ResourceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_empty_title_fails_validation(self):
        data = {
            "title": "   ",
            "description": "Empty title test",
            "category": self.category.pk,
        }
        form = ResourceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_missing_category_fails_validation(self):
        data = {
            "title": "Valid Title Here",
            "description": "No category provided",
        }
        form = ResourceForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_form_saves_model_instance(self):
        data = {
            "title": "Clean Code",
            "description": "A handbook of agile software craftsmanship",
            "resource_type": "Book",
            "category": self.category.pk,
            "available": True,
        }
        form = ResourceForm(data=data)
        self.assertTrue(form.is_valid())
        saved_instance = form.save()
        self.assertEqual(saved_instance.title, "Clean Code")
        self.assertEqual(Resource.objects.filter(title="Clean Code").count(), 1)


class ResourceDetailViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Computer Science")
        cls.resource = Resource.objects.create(
            title="Algorithms 101",
            description="Introduction to Big O",
            resource_type="Article",
            category=cls.category,
            available=True,
        )

    def test_anonymous_can_view_detail(self):
        response = self.client.get(
            reverse("pages:resource-detail", kwargs={"pk": self.resource.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/resource_detail.html")

    def test_detail_view_shows_resource_info(self):
        response = self.client.get(
            reverse("pages:resource-detail", kwargs={"pk": self.resource.pk})
        )
        self.assertContains(response, "Algorithms 101")
        self.assertContains(response, "Introduction to Big O")
        self.assertContains(response, "Computer Science")
        self.assertContains(response, "Available")

    def test_detail_view_404_for_nonexistent_resource(self):
        response = self.client.get(
            reverse("pages:resource-detail", kwargs={"pk": 99999})
        )
        self.assertEqual(response.status_code, 404)

    def test_detail_view_action_links_for_editor_vs_anonymous(self):
        # Anonymous user should not see Edit or Delete buttons
        anon_resp = self.client.get(
            reverse("pages:resource-detail", kwargs={"pk": self.resource.pk})
        )
        self.assertNotContains(anon_resp, "Edit resource")
        self.assertNotContains(anon_resp, "Delete")


class ResourceCreateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="DevOps")
        content_type = ContentType.objects.get_for_model(Resource)

        cls.perm_add = Permission.objects.get(
            content_type=content_type, codename="add_resource"
        )
        cls.perm_view = Permission.objects.get(
            content_type=content_type, codename="view_resource"
        )

        cls.reviewers = Group.objects.create(name="Catalog reviewers")
        cls.reviewers.permissions.add(cls.perm_view)

        cls.editors = Group.objects.create(name="Catalog editors")
        cls.editors.permissions.add(cls.perm_view, cls.perm_add)

    def setUp(self):
        self.regular_user = get_user_model().objects.create_user(
            username="regular_user", password="Password123!"
        )
        self.reviewer_user = get_user_model().objects.create_user(
            username="reviewer_user", password="Password123!"
        )
        self.reviewer_user.groups.add(self.reviewers)

        self.editor_user = get_user_model().objects.create_user(
            username="editor_user", password="Password123!"
        )
        self.editor_user.groups.add(self.editors)

    def test_anonymous_create_redirects_to_login(self):
        response = self.client.get(reverse("pages:resource-create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("pages:login"), response.url)

    def test_regular_user_cannot_access_create(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse("pages:resource-create"))
        self.assertEqual(response.status_code, 403)

    def test_reviewer_cannot_access_create(self):
        self.client.force_login(self.reviewer_user)
        response = self.client.get(reverse("pages:resource-create"))
        self.assertEqual(response.status_code, 403)

    def test_editor_can_access_create_form(self):
        self.client.force_login(self.editor_user)
        response = self.client.get(reverse("pages:resource-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/resource_form.html")

    def test_editor_valid_post_creates_resource(self):
        self.client.force_login(self.editor_user)
        response = self.client.post(
            reverse("pages:resource-create"),
            {
                "title": "Docker in Action",
                "description": "Container virtualization essentials",
                "resource_type": "Book",
                "category": self.category.pk,
                "available": True,
            },
        )
        new_resource = Resource.objects.get(title="Docker in Action")
        self.assertRedirects(
            response,
            reverse("pages:resource-detail", kwargs={"pk": new_resource.pk}),
        )
        self.assertEqual(new_resource.category, self.category)

    def test_editor_invalid_post_shows_form_errors(self):
        self.client.force_login(self.editor_user)
        response = self.client.post(
            reverse("pages:resource-create"),
            {
                "title": "X",  # Too short
                "category": self.category.pk,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Resource.objects.filter(title="X").exists())
        self.assertTrue(response.context["form"].has_error("title"))
        self.assertIn(
            "The title must contain at least 3 characters.",
            response.context["form"].errors["title"],
        )


class ResourceUpdateViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Databases")
        cls.resource = Resource.objects.create(
            title="SQL Performance Explained",
            description="Index tuning guide",
            resource_type="Book",
            category=cls.category,
            available=True,
        )

        content_type = ContentType.objects.get_for_model(Resource)
        cls.perm_change = Permission.objects.get(
            content_type=content_type, codename="change_resource"
        )
        cls.perm_view = Permission.objects.get(
            content_type=content_type, codename="view_resource"
        )

        cls.reviewers = Group.objects.create(name="Catalog reviewers")
        cls.reviewers.permissions.add(cls.perm_view)

        cls.editors = Group.objects.create(name="Catalog editors")
        cls.editors.permissions.add(cls.perm_view, cls.perm_change)

    def setUp(self):
        self.regular_user = get_user_model().objects.create_user(
            username="regular_update", password="Password123!"
        )
        self.reviewer_user = get_user_model().objects.create_user(
            username="reviewer_update", password="Password123!"
        )
        self.reviewer_user.groups.add(self.reviewers)

        self.editor_user = get_user_model().objects.create_user(
            username="editor_update", password="Password123!"
        )
        self.editor_user.groups.add(self.editors)

    def test_anonymous_update_redirects_to_login(self):
        response = self.client.get(
            reverse("pages:resource-edit", kwargs={"pk": self.resource.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("pages:login"), response.url)

    def test_regular_user_cannot_access_update(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(
            reverse("pages:resource-edit", kwargs={"pk": self.resource.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_reviewer_cannot_access_update(self):
        self.client.force_login(self.reviewer_user)
        response = self.client.get(
            reverse("pages:resource-edit", kwargs={"pk": self.resource.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_editor_can_access_update_form(self):
        self.client.force_login(self.editor_user)
        response = self.client.get(
            reverse("pages:resource-edit", kwargs={"pk": self.resource.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/resource_form.html")
        self.assertContains(response, "SQL Performance Explained")

    def test_editor_valid_post_updates_resource(self):
        self.client.force_login(self.editor_user)
        original_pk = self.resource.pk
        response = self.client.post(
            reverse("pages:resource-edit", kwargs={"pk": original_pk}),
            {
                "title": "SQL Performance 2nd Edition",
                "description": "Updated indexing guide",
                "resource_type": "eBook",
                "category": self.category.pk,
                "available": False,
            },
        )
        self.assertRedirects(
            response,
            reverse("pages:resource-detail", kwargs={"pk": original_pk}),
        )
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.pk, original_pk)
        self.assertEqual(self.resource.title, "SQL Performance 2nd Edition")
        self.assertFalse(self.resource.available)
        self.assertEqual(Resource.objects.filter(pk=original_pk).count(), 1)

    def test_update_404_for_nonexistent_resource(self):
        self.client.force_login(self.editor_user)
        response = self.client.get(
            reverse("pages:resource-edit", kwargs={"pk": 99999})
        )
        self.assertEqual(response.status_code, 404)


class ResourceDeleteViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Security")
        content_type = ContentType.objects.get_for_model(Resource)

        cls.perm_delete = Permission.objects.get(
            content_type=content_type, codename="delete_resource"
        )
        cls.perm_view = Permission.objects.get(
            content_type=content_type, codename="view_resource"
        )

        cls.reviewers = Group.objects.create(name="Catalog reviewers")
        cls.reviewers.permissions.add(cls.perm_view)

        cls.editors = Group.objects.create(name="Catalog editors")
        cls.editors.permissions.add(cls.perm_view, cls.perm_delete)

    def setUp(self):
        self.resource = Resource.objects.create(
            title="Web Application Security",
            category=self.category,
            available=True,
        )
        self.regular_user = get_user_model().objects.create_user(
            username="regular_delete", password="Password123!"
        )
        self.reviewer_user = get_user_model().objects.create_user(
            username="reviewer_delete", password="Password123!"
        )
        self.reviewer_user.groups.add(self.reviewers)

        self.editor_user = get_user_model().objects.create_user(
            username="editor_delete", password="Password123!"
        )
        self.editor_user.groups.add(self.editors)

    def test_anonymous_delete_redirects_to_login(self):
        response = self.client.get(
            reverse("pages:resource-delete", kwargs={"pk": self.resource.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("pages:login"), response.url)

    def test_regular_user_cannot_access_delete(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(
            reverse("pages:resource-delete", kwargs={"pk": self.resource.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_reviewer_cannot_access_delete(self):
        self.client.force_login(self.reviewer_user)
        response = self.client.get(
            reverse("pages:resource-delete", kwargs={"pk": self.resource.pk})
        )
        self.assertEqual(response.status_code, 403)

    def test_editor_get_shows_confirmation_without_deleting(self):
        self.client.force_login(self.editor_user)
        response = self.client.get(
            reverse("pages:resource-delete", kwargs={"pk": self.resource.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/resource_confirm_delete.html")
        self.assertContains(response, "Web Application Security")
        # Resource must still exist after GET
        self.assertTrue(Resource.objects.filter(pk=self.resource.pk).exists())

    def test_editor_post_deletes_resource(self):
        self.client.force_login(self.editor_user)
        target_pk = self.resource.pk
        response = self.client.post(
            reverse("pages:resource-delete", kwargs={"pk": target_pk})
        )
        self.assertRedirects(response, reverse("pages:resources"))
        self.assertFalse(Resource.objects.filter(pk=target_pk).exists())
