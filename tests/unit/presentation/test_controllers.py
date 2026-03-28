import pytest

from src.application.use_cases import OnboardRepositoryUseCase
from src.infrastructure.gateways import RepositoryInformationExtractorGateway
from src.presentation.controllers import CommandLineInterfaceController


@pytest.fixture
def command_line_interface_controller() -> CommandLineInterfaceController:
    return CommandLineInterfaceController(
        onboard_repository_use_case=OnboardRepositoryUseCase(
            repository_information=RepositoryInformationExtractorGateway(),
        ),
    )


@pytest.mark.parametrize(
    argnames=("issue_body"),
    argvalues=[
        ("### Repository name\n\nmy-repository\n"),
        ("### Repository name\n\nmy_repository\n"),
    ],
)
def test_command_line_interface_controller_call(
    issue_body: str,
    command_line_interface_controller: CommandLineInterfaceController,
) -> None:
    command_line_interface_controller(issue_body)
