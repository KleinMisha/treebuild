"""Plain text characters in renderer"""

from treebuild.harvest.renderer import Connector, Renderer


class PlainTextRenderer(Renderer):
    """Implementation for standard format used by box drawings / tools like 'tree'/ 'eza'"""

    @property
    def _connectors(self) -> dict[Connector, str]:
        return {
            Connector.EMPTY: " " * 4,
            Connector.CONTINUATION: "│   ",
            Connector.MIDDLE_CHILD: "├── ",
            Connector.FINAL_CHILD: "└── ",
        }

    def _format_line(self, name: str, ancestor_is_last: list[bool]) -> str:
        before_node_name = "".join(
            self._connectors[Connector.EMPTY]
            if flag
            else self._connectors[Connector.CONTINUATION]
            for flag in ancestor_is_last[:-1]
        )
        connector = (
            self._connectors[Connector.FINAL_CHILD]
            if ancestor_is_last[-1]
            else self._connectors[Connector.MIDDLE_CHILD]
        )

        return before_node_name + connector + name
