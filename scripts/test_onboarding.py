from typing import TYPE_CHECKING

import pytest

from scripts.onboarding import (
    CommandLineInterfaceController,
    OnboardRepositoryUseCase,
    RepositoryInformationParserGateway,
    RepositoryInformationValidatorGateway,
    RepositoryDoesNotExistError
)

if TYPE_CHECKING:
    from scripts.onboarding import RepositoryInformationValueObject


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


class AWSUpdaterMock:
    def __init__(self) -> None:
        self._result: bool = False

    @property
    def result(self) -> bool:
        return self._result

    async def execute(self, repository_information_value_object: RepositoryInformationValueObject) -> None:
        if repository_information_value_object:
            self._result = True


@pytest.fixture
def check_repository_existence() -> CheckRepositoryExistenceMock:
    return CheckRepositoryExistenceMock("mock-token")


@pytest.fixture
def issue_message_sender() -> IssueMessageSenderMock:
    return IssueMessageSenderMock("mock-repository", 1, "mock-token")


@pytest.fixture
def close_issue() -> CloseIssueMock:
    return CloseIssueMock("mock-repository", 1, "mock-token")


@pytest.fixture
def aws_updater() -> AWSUpdaterMock:
    return AWSUpdaterMock()


@pytest.fixture
def command_line_interface_controller(
    check_repository_existence: CheckRepositoryExistenceMock,
    issue_message_sender: IssueMessageSenderMock,
    close_issue: CloseIssueMock,
    aws_updater: AWSUpdaterMock,
) -> CommandLineInterfaceController:
    return CommandLineInterfaceController(
        onboard_repository_use_case=OnboardRepositoryUseCase(
            check_repository_existence=check_repository_existence,
            issue_message_sender=issue_message_sender,
            close_issue=close_issue,
            repository_information_parser=RepositoryInformationParserGateway(),
            repository_information_validator=RepositoryInformationValidatorGateway(),
            aws_updater=aws_updater,
        ),
    )


@pytest.mark.parametrize(
    argnames=("issue_body", "expected_result", "is_repository_exist", "is_aws_updated", "is_issue_closed"),
    argvalues=[
        (
            "### Repository name\n\nmy-repository\n",
            {
                "result": "finished successfully",
                "repository": "my-repository",
            },
            True,
            True,
            True,
        ),
        (
            "### Repository name\n\nmy_repository\n",
            {
                "result": "finished successfully",
                "repository": "my_repository",
            },
            True,
            True,
            True,
        ),
        (
            "### Repository name\n\nmy.repository\n",
            {
                "result": "finished successfully",
                "repository": "my.repository",
            },
            True,
            True,
            True,
        ),
        (
            "### Repository name\n\nMyRepository1\n",
            {
                "result": "finished successfully",
                "repository": "MyRepository1",
            },
            True,
            True,
            True,
        ),
        (
            "### Repository name\n\nmy-repository",
            {
                "result": "finished successfully",
                "repository": "my-repository",
            },
            True,
            True,
            True,
        ),
        (
            "### Repository name\n\na\n",
            {
                "result": "finished successfully",
                "repository": "a",
            },
            True,
            True,
            True,
        ),
        (
            "### Repository name\n\n12345\n",
            {
                "result": "finished successfully",
                "repository": "12345",
            },
            True,
            True,
            True,
        ),
        (
            "### Repository name\nmy repo",
            {
                "result": "caught expected error",
                "error": "IssueBodyParseError",
                "context": "Can't find repository name in issue body.",
            },
            True,
            False,
            False,
        ),
        (
            "my repo",
            {
                "result": "caught expected error",
                "error": "IssueBodyParseError",
                "context": "Can't find repository name in issue body.",
            },
            True,
            False,
            False,
        ),
        (
            "### Repository name\n\n\nmy repo",
            {
                "result": "caught expected error",
                "error": "IssueBodyParseError",
                "context": "Repository name can't be empty.",
            },
            True,
            False,
            False,
        ),
        (
            "### Repository name\nmy repo\n\n",
            {
                "result": "caught expected error",
                "error": "IssueBodyParseError",
                "context": "Repository name can't be empty.",
            },
            True,
            False,
            False,
        ),
        (
            "### Repository name\n\nmy repo\n",
            {
                "result": "caught expected error",
                "error": "RepositoryInformationValidationError",
                "context": "Name can only contain letters, digits, hyphens, underscores and dots.",
            },
            True,
            False,
            False,
        ),
        (
            "### Repository name\n\nmy-repo; sudo rm -rf /\n",
            {
                "result": "caught expected error",
                "error": "RepositoryInformationValidationError",
                "context": "Name can only contain letters, digits, hyphens, underscores and dots.",
            },
            True,
            False,
            False,
        ),
        (
            "### Repository name\n\n-my-repo\n",
            {
                "result": "caught expected error",
                "error": "RepositoryInformationValidationError",
                "context": "Name can't start or end with hyphen.",
            },
            True,
            False,
            False,
        ),
        (
            "### Repository name\n\nmy-repo-\n",
            {
                "result": "caught expected error",
                "error": "RepositoryInformationValidationError",
                "context": "Name can't start or end with hyphen.",
            },
            True,
            False,
            False,
        ),
        (
            "### Repository name\n\n.my-repo\n",
            {
                "result": "caught expected error",
                "error": "RepositoryInformationValidationError",
                "context": "Name can't start or end with dot.",
            },
            True,
            False,
            False,
        ),
        (
            "### Repository name\n\nmy-repo.\n",
            {
                "result": "caught expected error",
                "error": "RepositoryInformationValidationError",
                "context": "Name can't start or end with dot.",
            },
            True,
            False,
            False,
        ),
        (
            f"### Repository name\n\n{'a' * 101}\n",
            {
                "result": "caught expected error",
                "error": "RepositoryInformationValidationError",
                "context": "Name must be between 1 and 100 characters.",
            },
            True,
            False,
            False,
        ),
        (
            "### Repository name\n\nmy-repository-2\n",
            {
                "result": "caught expected error",
                "error": "RepositoryDoesNotExistError",
                "context": "Can't find [mock/my-repository-2] repository.",
            },
            False,
            False,
            False,
        ),
    ],
)
def test_command_line_interface_controller_call(  # noqa: PLR0913
    issue_body: str,
    expected_result: dict[str, str],
    is_repository_exist: bool,  # noqa: FBT001
    is_aws_updated: bool,  # noqa: FBT001
    is_issue_closed: bool,  # noqa: FBT001
    check_repository_existence: CheckRepositoryExistenceMock,
    issue_message_sender: IssueMessageSenderMock,
    aws_updater: AWSUpdaterMock,
    close_issue: CloseIssueMock,
    command_line_interface_controller: CommandLineInterfaceController,
) -> None:
    check_repository_existence.result = is_repository_exist

    command_line_interface_controller(issue_body)

    assert issue_message_sender.result == expected_result
    assert aws_updater.result == is_aws_updated
    assert close_issue.result == is_issue_closed
