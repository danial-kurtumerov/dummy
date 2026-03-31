from json import dumps
from re import match
from typing import TYPE_CHECKING

from github import Github, GithubException

from src.domain.exceptions import IssueBodyParseError, RepositoryDoesNotExistError, RepositoryInformationValidationError
from src.domain.value_objects import RepositoryInformationValueObject

if TYPE_CHECKING:
    from github.Issue import Issue


class RepositoryInformationParserGateway:
    async def execute(self, issue_body: str) -> RepositoryInformationValueObject:
        lines: list[str] = issue_body.splitlines()

        return RepositoryInformationValueObject(
            name=self._parse_name(lines),
        )

    def _parse_name(self, lines: list[str]) -> str:
        try:
            name: str = lines[2].strip()
        except IndexError as exception:
            msg: str = "Can't find repository name in issue body."
            raise IssueBodyParseError(msg) from exception

        if not name:
            msg = "Repository name can't be empty."
            raise IssueBodyParseError(msg)

        return name


class RepositoryInformationValidatorGateway:
    _min_length: int = 1
    _max_length: int = 100

    async def execute(self, repository_information_value_object: RepositoryInformationValueObject) -> None:
        self._validate_name(repository_information_value_object.name)

    def _validate_name(self, name: str) -> None:
        if not self._min_length <= len(name) <= self._max_length:
            msg: str = "Name must be between 1 and 100 characters."
            raise RepositoryInformationValidationError(msg)

        if not match(r"^[a-zA-Z0-9._-]+$", name):
            msg = "Name can only contain letters, digits, hyphens, underscores and dots."
            raise RepositoryInformationValidationError(msg)

        if name.startswith("-") or name.endswith("-"):
            msg = "Name can't start or end with hyphen."
            raise RepositoryInformationValidationError(msg)

        if name.startswith(".") or name.endswith("."):
            msg = "Name can't start or end with dot."
            raise RepositoryInformationValidationError(msg)


class CheckRepositoryExistenceGateway:
    _organization: str = "danial-kurtumerov"
    _not_found_status: int = 404

    def __init__(
        self,
        token: str,
    ) -> None:
        self._github: Github = Github(token)

    async def execute(self, repository_information_value_object: RepositoryInformationValueObject) -> None:
        path: str = f"{self._organization}/{repository_information_value_object.name}"

        try:
            self._github.get_repo(path)

        except GithubException as exception:
            if exception.status == self._not_found_status:
                msg: str = f"Can't find [{path}] repository."
                raise RepositoryDoesNotExistError(msg) from exception


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


class CloseIssueGateway:
    _state: str = "closed"

    def __init__(
        self,
        repository_name: str,
        issue_number: int,
        token: str,
    ) -> None:
        self._issue: Issue = Github(token).get_repo(repository_name).get_issue(issue_number)

    async def execute(self) -> None:
        self._issue.edit(state=self._state)


class AWSUpdaterGateway:
    async def execute(self, repository_information_value_object: RepositoryInformationValueObject) -> None:
        if repository_information_value_object:
            ...
