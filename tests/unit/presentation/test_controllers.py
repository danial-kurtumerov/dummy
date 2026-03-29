import pytest

from src.application.use_cases import OnboardRepositoryUseCase
from src.infrastructure.gateways import RepositoryInformationParserGateway, RepositoryInformationValidatorGateway
from src.presentation.controllers import CommandLineInterfaceController
from tests.mocks.gateways import AWSUpdaterMock, CheckRepositoryExistenceMock, CloseIssueMock, IssueMessageSenderMock


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
        (
            "### Repository name",
            {
                "result": "caught expected error",
                "error": "IssueBodyParseError",
                "context": "Can't find repository name in issue body.",
            },
            False,
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
