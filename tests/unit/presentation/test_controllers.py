import pytest

from src.application.use_cases import OnboardRepositoryUseCase
from src.infrastructure.gateways import RepositoryInformationExtractorGateway
from src.presentation.controllers import CommandLineInterfaceController
from tests.mocks.gateways import IssueMessageSenderMock


@pytest.fixture
def issue_message_sender() -> IssueMessageSenderMock:
    return IssueMessageSenderMock("mock-repository", 1, "mock-token")


@pytest.fixture
def command_line_interface_controller(issue_message_sender: IssueMessageSenderMock) -> CommandLineInterfaceController:
    return CommandLineInterfaceController(
        onboard_repository_use_case=OnboardRepositoryUseCase(
            issue_message_sender=issue_message_sender,
            repository_information=RepositoryInformationExtractorGateway(),
        ),
    )


@pytest.mark.parametrize(
    argnames=("issue_body", "expected_result"),
    argvalues=[
        (
            "### Repository name\n\nmy-repository\n",
            {"result": "finished successfully", "repository": "my-repository"},
        ),
        (
            "### Repository name",
            {
                "result": "caught expected error",
                "error": "IssueBodyParseError",
                "context": "Can't find required parameters.",
            },
        ),
        (
            "### Repository name\n\nmy-repository.\n",
            {
                "result": "caught expected error",
                "error": "RepositoryNameValidationError",
                "context": "Name can't start or end with dot.",
            },
        ),
    ],
)
def test_command_line_interface_controller_call(
    issue_body: str,
    expected_result: dict[str, str],
    issue_message_sender: IssueMessageSenderMock,
    command_line_interface_controller: CommandLineInterfaceController,
) -> None:
    command_line_interface_controller(issue_body)

    assert issue_message_sender.result == expected_result
