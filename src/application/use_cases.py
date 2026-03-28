from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.interfaces import RepositoryInformationExtractorInterface
    from src.domain.value_objects import RepositoryInformationValueObject


class OnboardRepositoryUseCase:

    def __init__(
        self,
        repository_information: RepositoryInformationExtractorInterface,
    ) -> None:
        self._repository_information: RepositoryInformationExtractorInterface = repository_information

    async def execute(self, issue_body: str) -> None:
        repository_information: RepositoryInformationValueObject = await self._repository_information.execute(
            issue_body=issue_body,
        )

        if repository_information:
            ...
