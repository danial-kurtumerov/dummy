from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.domain.value_objects import RepositoryInformationValueObject


class RepositoryInformationExtractorInterface(Protocol):

    async def execute(self, issue_body: str) -> RepositoryInformationValueObject:
        ...


class IssueMessageSenderInterface(Protocol):

    async def execute(self, message: dict[str, str]) -> None:
        ...
