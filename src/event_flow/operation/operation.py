from typing import TYPE_CHECKING, Any, Callable, final

from ..message import Message
from ..shared import Components, Reference
from ..utils import internal
from ._internal import OperationInfo, OperationMeta
from .action_type import ActionType


@final
@internal
class Operation(metaclass=OperationMeta):
    if TYPE_CHECKING:
        __async_api_components__: Components
        __async_api_reference__: Reference

    def __init__(
        self,
        action: str,
        message: type[Message],
        handler: Callable[[Message], None] | None = None,
        *,
        channel: str,
        title: str | None,
        summary: str | None,
        description: str | None,
    ) -> None:
        self.action = action
        self.message = message
        self.handler = handler

        self.operation_info = self._make_operation_info(
            channel=channel,
            title=title,
            summary=summary,
            description=description,
        )

    def __call__(self, message: Message) -> None:
        if self.handler is None:
            raise RuntimeError(f"Handler not defined for {self.message}")

        self.handler(message)

    @property
    def operation_id(self) -> str:
        return f"{self.action}{self.message.__name__}"

    @classmethod
    def as_send(
        cls,
        message: type[Message],
        *,
        channel: str,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
    ) -> "Operation":
        return cls(
            action=ActionType.SEND,
            message=message,
            channel=channel,
            title=title,
            summary=summary,
            description=description,
        )

    @classmethod
    def as_receive(
        cls,
        message: type[Message],
        handler: Any,
        *,
        channel: str,
        title: str | None = None,
        summary: str | None = None,
        description: str | None = None,
    ) -> "Operation":
        return cls(
            action=ActionType.RECEIVE,
            message=message,
            handler=handler,
            channel=channel,
            title=title,
            summary=summary,
            description=description,
        )

    def sends(self, message_id: str) -> bool:
        return ActionType.SEND == self.action and message_id == self.message.__name__

    def receives(self, message_id: str) -> bool:
        return ActionType.RECEIVE == self.action and message_id == self.message.__name__

    def _make_operation_info(
        self,
        channel: str,
        title: str | None,
        summary: str | None,
        description: str | None,
    ) -> OperationInfo:
        operation_info = OperationInfo(channel=channel)
        if title is not None:
            operation_info["title"] = title
        if summary is not None:
            operation_info["summary"] = summary
        if description is not None:
            operation_info["description"] = description

        return operation_info
