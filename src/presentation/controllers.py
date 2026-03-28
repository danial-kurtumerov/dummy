from asyncio import run
from os import environ

from src.application.use_cases import OnboardRepositoryUseCase
from src.infrastructure.gateways import RepositoryInformationExtractorGateway


class CommandLineInterfaceController:

    def __init__(
        self,
        onboard_repository_use_case: OnboardRepositoryUseCase,
    ) -> None:
        self._onboard_repository_use_case: OnboardRepositoryUseCase = onboard_repository_use_case

    def __call__(self, issue_body: str) -> None:
        run(self._onboard_repository_use_case.execute(issue_body))

if __name__ == "__main__":
    app: CommandLineInterfaceController = CommandLineInterfaceController(
        onboard_repository_use_case=OnboardRepositoryUseCase(
            repository_information=RepositoryInformationExtractorGateway,
        ),
    )

    app(
        issue_body=environ.get("ONBOARD_REPO_MESSAGE", ""),
    )
