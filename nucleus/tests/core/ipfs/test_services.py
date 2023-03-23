import pytest
import nucleus.core.ipfs.service as service

from nucleus.core.ipfs.types import Service, Services
from nucleus.core.ipfs.constants import EXIT_SUCCESS
from nucleus.core.types import Any, URL, StdOut

PATH_CLI_PATCH = "nucleus.core.ipfs.service.IPFS"


class MockFailingCLI:
    msg: str

    def __init__(self, message: str):
        self.msg = message

    def __call__(self):
        # Check for raising error for any resulting fail
        raise RuntimeError(self.msg)


def test_register_service(mocker: Any):
    """Should return a valid output for valid service registration"""

    register_service = Service(
        name="edge", endpoint=URL("http://localhost"), key="abc123"
    )

    class MockCLI:
        cmd: str
        args: str

        def __call__(self):
            return StdOut(EXIT_SUCCESS, None)

    mocker.patch(PATH_CLI_PATCH, return_value=MockCLI())
    registered_service = service.register(register_service)

    assert registered_service == register_service


def test_services(mocker: Any):
    """Should return a valid output for valid service registration"""
    expected_services = [
        {
            "Service": "pinata",
            "ApiEndpoint": "https://api.pinata.cloud/psa",
        },
        {
            "Service": "pinata2",
            "ApiEndpoint": "https://api.pinata.cloud/psa",
        },
    ]

    class MockCLI:
        cmd: str
        args: str

        def __call__(self):
            return StdOut(EXIT_SUCCESS, {"RemoteServices": expected_services})

    mocker.patch(PATH_CLI_PATCH, return_value=MockCLI())
    registered_services = service.ls()
    services_iter = map(
        lambda x: Service(
            name=x["Service"],
            endpoint=URL(
                x["ApiEndpoint"]),
            key=None),
        expected_services,
    )

    assert list(registered_services.remote) == list(
        Services(remote=services_iter).remote
    )


def test_invalid_register_service(mocker: Any):
    """Should raise error for already registered service"""
    register_service = Service(
        name="edge",
        endpoint=URL("http://localhost"),
        key="abc123",
    )

    # Simulating an error returned by ipfs invalid service
    expected_issue = "Error: service already present"
    mocker.patch(PATH_CLI_PATCH, return_value=MockFailingCLI(expected_issue))
    with pytest.raises(RuntimeError):
        service.register(register_service)
