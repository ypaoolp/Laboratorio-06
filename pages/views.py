from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView

from .forms import ResourceForm
from .models import Resource


def home(request):
    context = {
        "welcome_message": "Explore learning resources and project ideas.",
    }
    return render(request, "pages/home.html", context)


def resources(request):
    context = {
        "resources": Resource.objects.select_related("category").all(),
    }
    return render(request, "pages/resources.html", context)


def about(request):
    context = {
        "purpose": "Practice URL routing, views, and templates.",
    }
    return render(request, "pages/about.html", context)


def signup(request):
    if request.user.is_authenticated:
        return redirect("pages:dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("pages:login")
    else:
        form = UserCreationForm()

    return render(request, "pages/signup.html", {"form": form})


@login_required
def dashboard(request):
    visit_count = request.session.get("dashboard_visits", 0) + 1
    request.session["dashboard_visits"] = visit_count

    return render(
        request,
        "pages/dashboard.html",
        {"visit_count": visit_count},
    )


@login_required
@permission_required("pages.view_resource", raise_exception=True)
def resource_review(request):
    context = {
        "resources": Resource.objects.select_related("category").all(),
    }
    return render(request, "pages/review.html", context)


@login_required
def dashboard_summary(request):
    total_resources = Resource.objects.count()
    available_resources = Resource.objects.filter(available=True).count()
    context = {
        "total_resources": total_resources,
        "available_resources": available_resources,
    }
    return render(request, "pages/summary.html", context)


# =============================================================================
# Class-Based Views (CBV) — Laboratorio 09 CRUD
# =============================================================================


class EditorAccessMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    Diferencia el acceso:
    - Redirige a login (HTTP 302) a usuarios anónimos.
    - Emite HTTP 403 Forbidden a usuarios autenticados sin el permiso requerido.
    """
    raise_exception = True

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect_to_login(
                self.request.get_full_path(),
                self.get_login_url(),
                self.get_redirect_field_name(),
            )
        return super().handle_no_permission()


class ResourceDetailView(DetailView):
    model = Resource
    template_name = "pages/resource_detail.html"
    context_object_name = "resource"


class ResourceCreateView(EditorAccessMixin, CreateView):
    model = Resource
    form_class = ResourceForm
    template_name = "pages/resource_form.html"
    permission_required = "pages.add_resource"

    def get_success_url(self):
        return reverse_lazy("pages:resource-detail", kwargs={"pk": self.object.pk})


class ResourceUpdateView(EditorAccessMixin, UpdateView):
    model = Resource
    form_class = ResourceForm
    template_name = "pages/resource_form.html"
    permission_required = "pages.change_resource"

    def get_success_url(self):
        return reverse_lazy("pages:resource-detail", kwargs={"pk": self.object.pk})


class ResourceDeleteView(EditorAccessMixin, DeleteView):
    model = Resource
    template_name = "pages/resource_confirm_delete.html"
    permission_required = "pages.delete_resource"
    success_url = reverse_lazy("pages:resources")
