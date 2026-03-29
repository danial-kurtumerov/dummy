from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from src.domain.value_objects import RepositoryInformationValueObject


class RepositoryInformationExtractorInterface(Protocol):

    async def execute(self, issue_body: str) -> RepositoryInformationValueObject:
        ...


class CheckRepositoryExistenceInterface(Protocol):

    async def execute(self, repository_information_value_object: RepositoryInformationValueObject) -> None:
        ...


class IssueMessageSenderInterface(Protocol):

    async def execute(self, message: dict[str, str]) -> None:
        ...

class CloseIssueInterface(Protocol):

    async def execute(self) -> None:
        ...
