import pytest
import pytest_asyncio

from src.domain.exceptions import IssueBodyParseError, RepositoryNameValidationError
from src.domain.value_objects import RepositoryInformationValueObject
from src.infrastructure.gateways import RepositoryInformationExtractorGateway


@pytest_asyncio.fixture
async def repository_information_extractor_gateway() -> RepositoryInformationExtractorGateway:
    return RepositoryInformationExtractorGateway()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=("issue_body", "expected_output"),
    argvalues=[
        ("### Repository name\n\nmy-repository\n", RepositoryInformationValueObject("my-repository")),
        ("### Repository name\n\nmy_repository\n", RepositoryInformationValueObject("my_repository")),
        ("### Repository name\n\nmy.repository\n", RepositoryInformationValueObject("my.repository")),
        ("### Repository name\n\nMyRepository1\n", RepositoryInformationValueObject("MyRepository1")),
        ("### Repository name\n\na\n", RepositoryInformationValueObject("a")),
        ("### Repository name\n\n12345\n", RepositoryInformationValueObject("12345")),
    ],
)
async def test_repository_information_extractor_gateway_execute(
    issue_body: str,
    expected_output: RepositoryInformationValueObject,
    repository_information_extractor_gateway: RepositoryInformationExtractorGateway,
) -> None:
    output: RepositoryInformationValueObject = await repository_information_extractor_gateway.execute(issue_body)

    assert output == expected_output


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=("issue_body", "error_message"),
    argvalues=[
        ("### Repository name\nmy repo", "Can't find required parameters."),
        ("my repo", "Can't find required parameters."),
    ],
)
async def test_repository_information_extractor_gateway_parse(
    issue_body: str,
    error_message: str,
    repository_information_extractor_gateway: RepositoryInformationExtractorGateway,
) -> None:
    with pytest.raises(IssueBodyParseError, match=error_message):
        await repository_information_extractor_gateway.execute(issue_body)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=("issue_body", "error_message"),
    argvalues=[
        (
            "### Repository name\n\nmy repo\n",
            "Name can only contain letters, digits, hyphens, underscores and dots.",
        ),
        (
            "### Repository name\n\nmy-repo; sudo rm -rf /\n",
            "Name can only contain letters, digits, hyphens, underscores and dots.",
        ),
        (
            "### Repository name\n\n-my-repo\n",
            "Name can't start or end with hyphen.",
        ),
        (
            "### Repository name\n\nmy-repo-\n",
            "Name can't start or end with hyphen.",
        ),
        (
            "### Repository name\n\n.my-repo\n.",
            "Name can't start or end with dot.",
        ),
        (
            "### Repository name\n\nmy-repo.\n.",
            "Name can't start or end with dot.",
        ),
        (
            f"### Repository name\n\n{'a'* 101}\n" ,
            "Name must be between 1 and 100 characters.",
        ),
    ],
)
async def test_repository_information_extractor_gateway_validate(
    issue_body: str,
    error_message: str,
    repository_information_extractor_gateway: RepositoryInformationExtractorGateway,
) -> None:
    with pytest.raises(RepositoryNameValidationError, match=error_message):
        await repository_information_extractor_gateway.execute(issue_body)
