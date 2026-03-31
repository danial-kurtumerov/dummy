# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pygithub==2.9.0",
# ]
# ///

from asyncio import run
from dataclasses import dataclass
from json import dumps
from os import environ
from re import match
from typing import TYPE_CHECKING, Protocol

from github import Github, GithubException

if TYPE_CHECKING:
    from github.Issue import Issue


@dataclass(slots=True, frozen=True)
class RepositoryInformationValueObject:
    name: str


class IssueBodyParseError(BaseException): ...


class RepositoryInformationValidationError(BaseException): ...


class RepositoryDoesNotExistError(BaseException): ...


class RepositoryInformationParserInterface(Protocol):
    async def execute(self, issue_body: str) -> RepositoryInformationValueObject: ...


class RepositoryInformationValidatorInterface(Protocol):
    async def execute(self, repository_information_value_object: RepositoryInformationValueObject) -> None: ...


class CheckRepositoryExistenceInterface(Protocol):
    async def execute(self, repository_information_value_object: RepositoryInformationValueObject) -> None: ...


class IssueMessageSenderInterface(Protocol):
    async def execute(self, message: dict[str, str]) -> None: ...


class CloseIssueInterface(Protocol):
    async def execute(self) -> None: ...


class AWSUpdaterInterface(Protocol):
    async def execute(self, repository_information_value_object: RepositoryInformationValueObject) -> None: ...


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


class OnboardRepositoryUseCase:
    def __init__(  # noqa: PLR0913
        self,
        check_repository_existence: CheckRepositoryExistenceInterface,
        issue_message_sender: IssueMessageSenderInterface,
        close_issue: CloseIssueInterface,
        repository_information_parser: RepositoryInformationParserInterface,
        repository_information_validator: RepositoryInformationValidatorInterface,
        aws_updater: AWSUpdaterInterface,
    ) -> None:
        self._check_repository_existence: CheckRepositoryExistenceInterface = check_repository_existence
        self._issue_message_sender: IssueMessageSenderInterface = issue_message_sender
        self._close_issue: CloseIssueInterface = close_issue
        self._repository_information_parser: RepositoryInformationParserInterface = repository_information_parser
        self._repository_information_validator: RepositoryInformationValidatorInterface = (
            repository_information_validator
        )
        self._aws_updater: AWSUpdaterInterface = aws_updater

    async def execute(self, issue_body: str) -> None:
        try:
            repo_information: RepositoryInformationValueObject = await self._repository_information_parser.execute(
                issue_body=issue_body,
            )

        except IssueBodyParseError as exception:
            await self._send_error_message_to_issue(exception)
            return

        try:
            await self._repository_information_validator.execute(repo_information)

        except RepositoryInformationValidationError as exception:
            await self._send_error_message_to_issue(exception)
            return

        if repo_information:
            try:
                await self._check_repository_existence.execute(repo_information)

            except RepositoryDoesNotExistError as exception:
                await self._send_error_message_to_issue(exception)
                return

            await self._aws_updater.execute(repo_information)
            await self._issue_message_sender.execute(
                {
                    "result": "finished successfully",
                    "repository": repo_information.name,
                },
            )

        await self._close_issue.execute()

    async def _send_error_message_to_issue(self, exception: BaseException) -> None:
        await self._issue_message_sender.execute(
            {
                "result": "caught expected error",
                "error": exception.__class__.__name__,
                "context": str(exception),
            },
        )


class CommandLineInterfaceController:
    def __init__(
        self,
        onboard_repository_use_case: OnboardRepositoryUseCase,
    ) -> None:
        self._onboard_repository_use_case: OnboardRepositoryUseCase = onboard_repository_use_case

    def __call__(self, issue_body: str) -> None:
        run(self._onboard_repository_use_case.execute(issue_body))


if __name__ == "__main__":
    repository_name: str = environ.get("REPO_NAME", "")
    issue_number: int = int(environ.get("ONBOARD_REPO_NUMBER", "0"))
    token: str = environ.get("GITHUB_TOKEN", "")
    issue_body: str = environ.get("ONBOARD_REPO_MESSAGE", "")

    app: CommandLineInterfaceController = CommandLineInterfaceController(
        onboard_repository_use_case=OnboardRepositoryUseCase(
            check_repository_existence=CheckRepositoryExistenceGateway(token),
            issue_message_sender=IssueMessageSenderGateway(repository_name, issue_number, token),
            close_issue=CloseIssueGateway(repository_name, issue_number, token),
            repository_information_parser=RepositoryInformationParserGateway(),
            repository_information_validator=RepositoryInformationValidatorGateway(),
            aws_updater=AWSUpdaterGateway(),
        ),
    )

    app(issue_body)
