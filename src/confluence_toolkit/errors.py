"""Domain exceptions exposed by the toolkit."""


class ToolkitError(Exception):
    """Base class for errors the CLI can present without a traceback."""


class ConfigurationError(ToolkitError):
    """Raised when required local configuration is missing or invalid."""


class ApiError(ToolkitError):
    """Raised when Confluence returns an unsuccessful API response."""


class InputError(ToolkitError):
    """Raised when a user-supplied page, URL, or CSV record is invalid."""
