import pytest
import pytest_asyncio

from src.domain.exceptions import IssueBodyParseError, RepositoryInformationValidationError
from src.domain.value_objects import RepositoryInformationValueObject
from src.infrastructure.gateways import RepositoryInformationParserGateway, RepositoryInformationValidatorGateway


@pytest_asyncio.fixture
async def repository_information_parser_gateway() -> RepositoryInformationParserGateway:
    return RepositoryInformationParserGateway()


@pytest_asyncio.fixture
async def repository_information_validator_gateway() -> RepositoryInformationValidatorGateway:
    return RepositoryInformationValidatorGateway()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=("issue_body", "expected_output"),
    argvalues=[
        ("### Repository name\n\nmy-repository\n", RepositoryInformationValueObject("my-repository")),
        ("### Repository name\n\nmy_repository\n", RepositoryInformationValueObject("my_repository")),
        ("### Repository name\n\nmy.repository\n", RepositoryInformationValueObject("my.repository")),
        ("### Repository name\n\nMyRepository1\n", RepositoryInformationValueObject("MyRepository1")),
        ("### Repository name\n\nmy-repository", RepositoryInformationValueObject("my-repository")),
        ("### Repository name\n\na\n", RepositoryInformationValueObject("a")),
        ("### Repository name\n\n12345\n", RepositoryInformationValueObject("12345")),
    ],
)
async def test_repository_information_parser_gateway_execute(
    issue_body: str,
    expected_output: RepositoryInformationValueObject,
    repository_information_parser_gateway: RepositoryInformationParserGateway,
) -> None:
    output: RepositoryInformationValueObject = await repository_information_parser_gateway.execute(issue_body)

    assert output == expected_output


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=("issue_body", "error_message"),
    argvalues=[
        ("### Repository name\nmy repo", "Can't find repository name in issue body."),
        ("my repo", "Can't find repository name in issue body."),
        ("### Repository name\n\n\nmy repo", "Repository name can't be empty."),
        ("### Repository name\nmy repo\n\n", "Repository name can't be empty."),
    ],
)
async def test_repository_information_parser_gateway_errors(
    issue_body: str,
    error_message: str,
    repository_information_parser_gateway: RepositoryInformationParserGateway,
) -> None:
    with pytest.raises(IssueBodyParseError, match=error_message):
        await repository_information_parser_gateway.execute(issue_body)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=("repository_information_value_object", "expected_output"),
    argvalues=[
        (RepositoryInformationValueObject("my-repository"), None),
        (RepositoryInformationValueObject("my_repository"), None),
        (RepositoryInformationValueObject("my.repository"), None),
        (RepositoryInformationValueObject("MyRepository1"), None),
        (RepositoryInformationValueObject("a"), None),
        (RepositoryInformationValueObject("12345"), None),
    ],
)
async def test_repository_information_validator_gateway_execute(
    repository_information_value_object: RepositoryInformationValueObject,
    expected_output: None,
    repository_information_validator_gateway: RepositoryInformationValidatorGateway,
) -> None:
    output: None = await repository_information_validator_gateway.execute(
        repository_information_value_object=repository_information_value_object,
    )

    assert output == expected_output


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=("repository_information_value_object", "error_message"),
    argvalues=[
        (
            RepositoryInformationValueObject("my repo"),
            "Name can only contain letters, digits, hyphens, underscores and dots.",
        ),
        (
            RepositoryInformationValueObject("my-repo; sudo rm -rf /\n"),
            "Name can only contain letters, digits, hyphens, underscores and dots.",
        ),
        (
            RepositoryInformationValueObject("-my-repo"),
            "Name can't start or end with hyphen.",
        ),
        (
            RepositoryInformationValueObject("my-repo-"),
            "Name can't start or end with hyphen.",
        ),
        (
            RepositoryInformationValueObject(".my-repo"),
            "Name can't start or end with dot.",
        ),
        (
            RepositoryInformationValueObject("my-repo."),
            "Name can't start or end with dot.",
        ),
        (
            RepositoryInformationValueObject(f"n{'a'* 101}"),
            "Name must be between 1 and 100 characters.",
        ),
    ],
)
async def test_repository_information_validator_gateway_errors(
    repository_information_value_object: RepositoryInformationValueObject,
    error_message: str,
    repository_information_validator_gateway: RepositoryInformationValidatorGateway,
) -> None:
    with pytest.raises(RepositoryInformationValidationError, match=error_message):
        await repository_information_validator_gateway.execute(repository_information_value_object)
