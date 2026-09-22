from collections.abc import Iterable

from observation.composition.factory import ProviderFactory
from observation.core.provider import ObservationProvider
from observation.registry.registry import ProviderRegistry


class ProviderComposer:
    """
    Coordinates provider construction and registration.

    The composer receives provider classes, delegates construction
    to ProviderFactory, and registers the resulting instances in
    ProviderRegistry.

    It does not discover providers or manage their lifecycle.
    """

    def __init__(
        self,
        factory: ProviderFactory,
        registry: ProviderRegistry,
    ) -> None:
        self._factory = factory
        self._registry = registry

    def compose(
        self,
        providers: Iterable[type[ObservationProvider]],
    ) -> list[ObservationProvider]:
        """
        Construct and register the supplied provider classes.
        """

        instances = self._factory.create(providers)

        for provider in instances:
            self._registry.register(provider)

        return instances