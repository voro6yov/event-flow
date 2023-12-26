from typing import TYPE_CHECKING, Callable, final

from ..message import Message
from ..operation import Operation
from ..shared import Components, Reference
from ..utils import external
from ._internal import ChannelInfo, ChannelMeta

EventHandler = Callable[[Message], None]


@final
@external
class Channel(metaclass=ChannelMeta):
    if TYPE_CHECKING:
        _messages: dict[str, dict[str, str]]
        __async_api_components__: Components
        __async_api_reference__: Reference

    def __init__(
        self,
        address: str,
        *,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
    ) -> None:
        self.address = address

        self.channel_info = self._make_channel_info(
            title=title,
            summary=summary,
            description=description,
        )

        self.operations: list[Operation] = []

    @property
    def channel_id(self) -> str:
        return self.address

    def publish(
        self,
        *,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
    ) -> Callable[[type[Message]], type[Message]]:
        def decorator(message: type[Message]) -> type[Message]:
            self._add_message(message)  # type: ignore
            self._add_operation(  # type: ignore
                Operation.as_send(
                    message,
                    channel=self.channel_id,
                    title=title,
                    summary=summary,
                    description=description,
                )
            )

            return message

        return decorator

    def subscribe(
        self,
        message: type[Message],
        *,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
    ) -> Callable[[EventHandler], EventHandler]:
        def decorator(handler: EventHandler) -> EventHandler:
            self._add_message(message)  # type: ignore
            self._add_operation(  # type: ignore
                Operation.as_receive(
                    message,
                    handler,
                    channel=self.channel_id,
                    title=title,
                    summary=summary,
                    description=description,
                )
            )

            return handler

        return decorator

    def sends(self, message: Message) -> bool:
        return (
            next(
                filter(lambda o: o.sends(message.message_id), self.operations),
                None,
            )
            is not None
        )

    def find_operation(self, address: str, message_id: str) -> Operation | None:
        return next(
            filter(
                lambda o: address == self.address and o.receives(message_id),
                self.operations,
            ),
            None,
        )

    def _make_channel_info(
        self,
        title: str | None,
        summary: str | None,
        description: str | None,
    ) -> ChannelInfo:
        channel_info = ChannelInfo()
        if title is not None:
            channel_info["title"] = title
        if summary is not None:
            channel_info["summary"] = summary
        if description is not None:
            channel_info["description"] = description

        return channel_info
