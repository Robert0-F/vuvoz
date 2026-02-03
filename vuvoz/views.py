"""
Catch-all view to serve Vue SPA: return index.html for non-API routes.
"""
from pathlib import Path

from django.http import FileResponse, Http404
from django.views import View


class VueSPAView(View):
    """Serve frontend/dist/index.html for SPA routing (all non-API paths)."""

    def get(self, request, *_args, **_kwargs):
        index_path = Path(__file__).resolve().parent.parent / 'frontend' / 'dist' / 'index.html'
        if not index_path.exists():
            raise Http404("Frontend not built. Run: npm run build in frontend/")
        return FileResponse(
            open(index_path, 'rb'),
            content_type='text/html',
        )
