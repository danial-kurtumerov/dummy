from typing import TYPE_CHECKING

from src.domain.exceptions import IssueBodyParseError, RepositoryDoesNotExistError, RepositoryInformationValidationError

if TYPE_CHECKING:
    from src.domain.interfaces import (
        AWSUpdaterInterface,
        CheckRepositoryExistenceInterface,
        CloseIssueInterface,
        IssueMessageSenderInterface,
        RepositoryInformationParserInterface,
        RepositoryInformationValidatorInterface,
    )
    from src.domain.value_objects import RepositoryInformationValueObject


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
