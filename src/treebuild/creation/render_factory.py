"""Renderers to select from"""

from enum import StrEnum, auto

from treebuild.creation.plain_text_renderer import PlainTextRenderer
from treebuild.creation.renderer import Renderer


class RenderMethod(StrEnum):
    PLAIN = auto()


RENDERERS: dict[RenderMethod, Renderer] = {RenderMethod.PLAIN: PlainTextRenderer()}


def get_renderer(method: RenderMethod) -> Renderer:
    return RENDERERS[method]
