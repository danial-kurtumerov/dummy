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
