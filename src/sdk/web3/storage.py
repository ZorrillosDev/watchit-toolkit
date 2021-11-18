import requests
from ipfshttpclient.exceptions import ErrorResponse
from src.sdk import logger, media
from src.sdk.constants import (
    VALIDATE_SSL,
    PINATA_API_SECRET,
    PINATA_API_KEY,
    PINATA_ENDPOINT,
    PINATA_PSA,
    PINATA_SERVICE,
    PINATA_API_JWT,
)

# Session keep alive
session = requests.Session()


def _find_service_in_list(service):
    """
    Check if "pinata" is a pin remote service in node
    :param service: Current processed Service dic
    :return: Tuple with value found or tuple with None (None,) || (pinata,)
    """
    return next(
        (
            i["Service"]
            for i in service["RemoteServices"]
            if i["Service"] == PINATA_SERVICE
        ),
        None,
    )


def valid_registered_service():
    """
    Check if pinata service is already registered
    :return: False if not registered else True
    """
    ipfs_api_client = media.ingest.ipfs.get_client()
    args = (PINATA_SERVICE, PINATA_PSA, PINATA_API_JWT)
    registered_services = ipfs_api_client.request(
        "/pin/remote/service/ls", args, decoder="json"
    )

    # Map result from registered services and search for "pinata"
    find_registered_service = map(_find_service_in_list, registered_services)
    return PINATA_SERVICE in tuple(filter(None, find_registered_service))


def pin_remote(cid: str, **kwargs):
    """
    Pin cid into edge pinata remote cache
    :param cid: the cid to pin
    :return
    """

    if not valid_registered_service():
        register_service()

    try:
        args = (cid,)
        ipfs_api_client = media.ingest.ipfs.get_client()
        kwargs.setdefault("opts", {"service": PINATA_SERVICE, "background": False})
        return ipfs_api_client.request("/pin/remote/add", args, decoder="json", **kwargs)
    except ErrorResponse:
        logger.log.warning('Object already pinned to pinata')
        logger.log.info('Please remove or replace existing pin object')


def register_service():
    """
    Register service in ipfs node
    :return: request result according to
    http://docs.ipfs.io.ipns.localhost:8080/reference/http/api/#api-v0-pin-remote-service-add
    """
    if valid_registered_service():
        logger.log.warning("Service already registered")
        return

    ipfs_api_client = media.ingest.ipfs.get_client()
    args = (PINATA_SERVICE, PINATA_PSA, PINATA_API_JWT)
    logger.log.info("Registering pinata service")
    return ipfs_api_client.request("/pin/remote/service/add", args, decoder="json")


def check_pinata_status():
    # Start http session
    response = session.get(
        f"{PINATA_ENDPOINT}/data/testAuthentication",
        verify=VALIDATE_SSL,
        headers={
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_API_SECRET,
        },
    )

    # Check status for response
    return response.status_code == requests.codes.ok and valid_registered_service()
