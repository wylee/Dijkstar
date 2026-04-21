from starlette.templating import Jinja2Templates

from ..conf import settings

templates = Jinja2Templates(directory=settings.template_directory)
TemplateResponse = templates.TemplateResponse


def render_template(request, path, context=None):
    """Render template at path with the given context."""
    return TemplateResponse(request, path, context)
