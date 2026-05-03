from abc import ABC, abstractmethod
from pathlib import Path


class AgentIntegration(ABC):
    """Base class for AI coding agent integrations.

    Subclass this to add support for a new agent (e.g. Cursor, Copilot, Devin).
    Each integration is responsible for setting up whatever config files or
    server processes that agent needs to consume codebrief's output.
    """

    #: Short identifier used on the CLI, e.g. "claude-code", "cursor".
    name: str
    #: One-line description shown in `codebrief agents list`.
    description: str

    @abstractmethod
    def setup(self, project_dir: Path) -> None:
        """Write integration config files into *project_dir*.

        Should be idempotent — safe to run more than once.
        """

    def __repr__(self) -> str:
        return f"<AgentIntegration name={self.name!r}>"
