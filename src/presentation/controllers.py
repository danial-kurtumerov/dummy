from asyncio import run
from os import environ

from src.application.use_cases import OnboardRepositoryUseCase
from src.infrastructure.gateways import (
    CheckRepositoryExistenceGateway,
    CloseIssueGateway,
    IssueMessageSenderGateway,
    RepositoryInformationExtractorGateway,
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
            repository_information=RepositoryInformationExtractorGateway(),
        ),
    )

    app(issue_body)
