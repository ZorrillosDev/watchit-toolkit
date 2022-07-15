import pytest
from typing import Any
from src.core.storage.types import EdgeService, EdgeServices
from src.core.storage.services import services, register
from src.core.exceptions import IPFSFailedExecution


class MockFailingCLI:
    msg: str

    def __init__(self, message: str):
        self.msg = message

    def __call__(self):
        # Check for raising error for any resulting fail
        raise IPFSFailedExecution(self.msg)


def test_register_service(mocker: Any):
    """Should return a valid output for valid service registration"""

    register_service = EdgeService(
        **{
            "service": "edge",
            "endpoint": "http://localhost",
            "key": "abc123",
        }
    )

    class MockCLI:
        cmd: str
        args: str

        def __call__(self):
            return {"output": None}

    mocker.patch("src.core.storage.services.CLI", return_value=MockCLI())
    registered_service = register(register_service)

    assert registered_service == registered_service


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
            return {"output": {"RemoteServices": expected_services}}

    mocker.patch("src.core.storage.services.CLI", return_value=MockCLI())
    registered_services = services()
    services_iter = map(
        lambda x: EdgeService(
            service=x["Service"],
            endpoint=x["ApiEndpoint"],
        ),
        expected_services,
    )
    
    assert list(registered_services["remote"]) == list(
        EdgeServices(remote=services_iter)["remote"]
    )


def test_invalid_register_service(mocker: Any):
    """Should raise error for already registered service"""
    register_service = EdgeService(
        **{
            "service": "edge",
            "endpoint": "http://localhost",
            "key": "abc123",
        }
    )

    # Simulating an error returned by ipfs invalid service
    expected_issue = "Error: service already present"
    mocker.patch(
        "src.core.storage.services.CLI", return_value=MockFailingCLI(expected_issue)
    )
    with pytest.raises(IPFSFailedExecution):
        register(register_service)

