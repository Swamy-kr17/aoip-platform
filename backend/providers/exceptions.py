class ProviderError(Exception):
    """Base exception for AOIP provider failures."""


class ProviderUnavailableError(ProviderError):
    """Raised when a provider is temporarily unavailable."""


class ProviderRateLimitError(ProviderError):
    """Raised when a provider rate limit or quota is exceeded."""


class ProviderAuthenticationError(ProviderError):
    """Raised when provider authentication fails."""


class ProviderConfigurationError(ProviderError):
    """Raised when a provider is not configured correctly."""


class ProviderDownstreamError(ProviderError):
    """Raised for an unexpected downstream provider failure."""
