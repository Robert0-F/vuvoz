"""
Catch-all view to serve Vue SPA: return index.html for non-API routes.
"""
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.views import View


class VueSPAView(View):
    """Serve index.html for SPA routing (from frontend/dist or from collectstatic)."""

    def get(self, request, *_args, **_kwargs):
        # Prefer frontend/dist (local/dev and Docker), then staticfiles (e.g. after collectstatic only)
        base_dir = Path(settings.BASE_DIR)
        index_path = base_dir / 'frontend' / 'dist' / 'index.html'
        if not index_path.exists() and settings.STATIC_ROOT:
            index_path = Path(settings.STATIC_ROOT) / 'index.html'
        if not index_path.exists():
            raise Http404("Frontend not built. Run: cd frontend && npm run build, then python manage.py collectstatic")
        return FileResponse(
            open(index_path, 'rb'),
            content_type='text/html',
        )
