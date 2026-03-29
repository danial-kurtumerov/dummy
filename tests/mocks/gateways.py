from typing import TYPE_CHECKING

from src.domain.exceptions import RepositoryDoesNotExistError

if TYPE_CHECKING:
    from src.domain.value_objects import RepositoryInformationValueObject


class CheckRepositoryExistenceMock:

    _organization: str = "mock"

    def __init__(
        self,
        token: str,
    ) -> None:
        if token:
            ...

        self._result: bool = True

    async def execute(self, repository_information_value_object: RepositoryInformationValueObject) -> None:
        path: str = f"{self._organization}/{repository_information_value_object.name}"

        if not self._result:
            msg: str = f"Can't find [{path}] repository."
            raise RepositoryDoesNotExistError(msg)

    @property
    def result(self) -> bool:
        return self._result

    @result.setter
    def result(self, value: bool) -> None:
        self._result = value

class IssueMessageSenderMock:

    def __init__(
        self,
        repository_name: str,
        issue_number: int,
        token: str,
    ) -> None:
        if repository_name and issue_number and token:
            ...

        self._result: dict = {}

    async def execute(self, message: dict[str, str]) -> None:
        self._result = message

    @property
    def result(self) -> dict[str, str]:
        return self._result


class CloseIssueMock:

    def __init__(
        self,
        repository_name: str,
        issue_number: int,
        token: str,
    ) -> None:
        if repository_name and issue_number and token:
            ...

        self._result: bool = False

    async def execute(self) -> None:
        self._result = True

    @property
    def result(self) -> bool:
        return self._result
