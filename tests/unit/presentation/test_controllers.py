import pytest

from src.application.use_cases import OnboardRepositoryUseCase
from src.infrastructure.gateways import RepositoryInformationParserGateway, RepositoryInformationValidatorGateway
from src.presentation.controllers import CommandLineInterfaceController
from tests.mocks.gateways import CheckRepositoryExistenceMock, CloseIssueMock, IssueMessageSenderMock


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
def command_line_interface_controller(
    check_repository_existence: CheckRepositoryExistenceMock,
    issue_message_sender: IssueMessageSenderMock,
    close_issue: CloseIssueMock,
) -> CommandLineInterfaceController:
    return CommandLineInterfaceController(
        onboard_repository_use_case=OnboardRepositoryUseCase(
            check_repository_existence=check_repository_existence,
            issue_message_sender=issue_message_sender,
            close_issue=close_issue,
            repository_information_parser=RepositoryInformationParserGateway(),
            repository_information_validator=RepositoryInformationValidatorGateway(),
        ),
    )


@pytest.mark.parametrize(
    argnames=("issue_body", "expected_result", "repository_exists", "is_issue_closed"),
    argvalues=[
        (
            "### Repository name\n\nmy-repository\n",
            {"result": "finished successfully", "repository": "my-repository"},
            True,
            True,
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
        ),
        (
            "### Repository name",
            {
                "result": "caught expected error",
                "error": "IssueBodyParseError",
                "context": "Can't find repository name in issue body.",
            },
            False,
            False,
        ),
        (
            "### Repository name\n\nmy-repository.\n",
            {
                "result": "caught expected error",
                "error": "RepositoryInformationValidationError",
                "context": "Name can't start or end with dot.",
            },
            False,
            False,
        ),
        (
            "### Repository name\n\nmy-repository; sudo rm -rf /\n",
            {
                "result": "caught expected error",
                "error": "RepositoryInformationValidationError",
                "context": "Name can only contain letters, digits, hyphens, underscores and dots.",
            },
            False,
            False,
        ),
    ],
)
def test_command_line_interface_controller_call(  # noqa: PLR0913
    issue_body: str,
    expected_result: dict[str, str],
    repository_exists: bool,  # noqa: FBT001
    is_issue_closed: bool,  # noqa: FBT001
    check_repository_existence: CheckRepositoryExistenceMock,
    issue_message_sender: IssueMessageSenderMock,
    close_issue: CloseIssueMock,
    command_line_interface_controller: CommandLineInterfaceController,
) -> None:
    check_repository_existence.result = repository_exists

    command_line_interface_controller(issue_body)

    assert issue_message_sender.result == expected_result
    assert close_issue.result == is_issue_closed
