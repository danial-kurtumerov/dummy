from typing import TYPE_CHECKING

from src.domain.exceptions import IssueBodyParseError, RepositoryNameValidationError

if TYPE_CHECKING:
    from src.domain.interfaces import (
        CloseIssueInterface,
        IssueMessageSenderInterface,
        RepositoryInformationExtractorInterface,
    )
    from src.domain.value_objects import RepositoryInformationValueObject


class OnboardRepositoryUseCase:

    def __init__(
        self,
        issue_message_sender: IssueMessageSenderInterface,
        close_issue: CloseIssueInterface,
        repository_information: RepositoryInformationExtractorInterface,
    ) -> None:
        self._issue_message_sender: IssueMessageSenderInterface = issue_message_sender
        self._close_issue: CloseIssueInterface = close_issue
        self._repository_information: RepositoryInformationExtractorInterface = repository_information

    async def execute(self, issue_body: str) -> None:
        try:
            repository_information: RepositoryInformationValueObject = await self._repository_information.execute(
                issue_body=issue_body,
            )

        except (IssueBodyParseError, RepositoryNameValidationError) as exception:
            await self._issue_message_sender.execute({
                "result": "caught expected error",
                "error": exception.__class__.__name__,
                "context": str(exception),
            })

            return

        if repository_information:
            await self._issue_message_sender.execute({
                "result": "finished successfully",
                "repository": repository_information.name,
            })

        await self._close_issue.execute()
