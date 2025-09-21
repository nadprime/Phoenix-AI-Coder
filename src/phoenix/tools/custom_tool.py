from crewai_tools import BaseTool

class PlaceholderTool(BaseTool):
    name: str = "Placeholder"
    description: str = "This tool does nothing yet."

    def _run(self, *args, **kwargs):
        return "Placeholder response"