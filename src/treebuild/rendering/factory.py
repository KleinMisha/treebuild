"""Renderers to select from"""

from enum import StrEnum, auto

from treebuild.rendering.plain_text_renderer import PlainTextRenderer
from treebuild.rendering.renderer import Renderer


class RenderMethod(StrEnum):
    PLAIN = auto()


RENDERERS: dict[RenderMethod, Renderer] = {RenderMethod.PLAIN: PlainTextRenderer()}


def get_renderer(method: RenderMethod) -> Renderer:
    return RENDERERS[method]
