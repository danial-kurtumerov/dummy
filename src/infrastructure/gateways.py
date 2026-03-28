from json import dumps
from re import match
from typing import TYPE_CHECKING

from github import Github

from src.domain.exceptions import IssueBodyParseError, RepositoryNameValidationError
from src.domain.value_objects import RepositoryInformationValueObject

if TYPE_CHECKING:
    from github.Issue import Issue


class RepositoryInformationExtractorGateway:
    _min_length: int = 1
    _max_length: int = 100

    async def execute(self, issue_body: str) -> RepositoryInformationValueObject:
        parameters: dict[str, str] = self._parse(issue_body)
        self._validate(parameters)

        return RepositoryInformationValueObject(**parameters)

    def _parse(self, issue_body: str) -> dict[str, str]:
        lines: list[str] = issue_body.splitlines()

        try:
            parameters: dict[str, str] = {"name": lines[2].strip()}
        except IndexError as exception:
            msg: str = "Can't find required parameters."
            raise IssueBodyParseError(msg) from exception

        return parameters

    def _validate(self, parameters: dict[str, str]) -> None:
        self._validate_name(parameters["name"])

    def _validate_name(self, name: str) -> None:
        if not self._min_length <= len(name) <= self._max_length:
            msg: str = "Name must be between 1 and 100 characters."
            raise RepositoryNameValidationError(msg)

        if not match(r"^[a-zA-Z0-9._-]+$", name):
            msg = "Name can only contain letters, digits, hyphens, underscores and dots."
            raise RepositoryNameValidationError(msg)

        if name.startswith("-") or name.endswith("-"):
            msg = "Name can't start or end with hyphen."
            raise RepositoryNameValidationError(msg)

        if name.startswith(".") or name.endswith("."):
            msg = "Name can't start or end with dot."
            raise RepositoryNameValidationError(msg)


class IssueMessageSenderGateway:

    def __init__(
        self,
        repository_name: str,
        issue_number: int,
        token: str,
    ) -> None:
        self._issue: Issue = Github(token).get_repo(repository_name).get_issue(issue_number)

    async def execute(self, message: dict[str, str]) -> None:
        self._issue.create_comment(f"```json\n{dumps(message, ensure_ascii=False, indent=4)}\n```")
