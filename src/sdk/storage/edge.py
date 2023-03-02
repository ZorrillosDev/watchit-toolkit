import requests

from src.core.types import Iterator, CID, Any, JSON
from .types import Edge, Service, Pin, Response, Session, Headers
from .constants import ESTUARY_API_PIN, ESTUARY_API_PUBLIC
from .exceptions import EdgePinException


# ESTd7a0cf19-db87-42f2-9d0b-4a462c6057bfARY


def _pin_factory(raw_pin: JSON):
    """Pin factory from raw pin list

    :param raw_pin: dictionary with pin information
    :return: Pin object
    :rtype: Pin
    """
    pin = raw_pin.get("pin", {})
    status = raw_pin.get("status", "fail")
    # pin subfields
    # ref: https://docs.estuary.tech/Reference/SwaggerUI#/pinning/get_pinning_pins
    name = pin.get("name", "estuary")
    cid = pin.get("cid", CID(""))
    return Pin(cid, status, name)


def _enhanced_response(res: Response) -> JSON:
    """Amplifier helper function to handle response from Estuary API

    :param res: expected response
    :return: json response
    :rtype: JSON
    :raises EdgePinException if an error occurs during request
    """

    # expected response as json
    response = res.json()
    # Failing during pin request
    if response.status_code > requests.codes.ok:
        error_description = response.get("details", "")
        raise EdgePinException(f"exception raised during request: {error_description}")

    return response


class Estuary(Edge):
    _service: Service
    _http: Session
    _headers: Headers

    def __init__(self, service: Service):
        self._http = Session()
        self._service = service
        self._headers = {"Authorization": f"Bearer {service.key}"}

    def _ls_records(self) -> JSON:
        """Return pinned records.
        We use this method to fetch pin ids.
        A proper usage could be fetch then filter CID to find corresponding pin id

        :return: list of pinned record
        :rtype: JSON
        :raises EdgePinException if an error occurs during request
        """
        req = self._http.get(
            ESTUARY_API_PIN,
            headers=self._headers,
        )

        # expected response as json
        response = _enhanced_response(req)
        return response.get("results", [])

    def _content_by_cid(self, cid: CID) -> JSON:
        """Collect details from estuary based on CID
        ref: https://docs.estuary.tech/Reference/SwaggerUI#/public/get_public_by_cid__cid_

        :param cid: cid to retrieve details
        :return: cid content details
        :rtype: JSON
        :raises EdgePinException: if pin request fails
        """

        req = self._http.get(
            f"{ESTUARY_API_PUBLIC}/by-cid/",
            headers=self._headers,
        )

        # expected response as json
        response = _enhanced_response(req)
        return response.get("content", {})

    def pin(self, cid: CID, **kwargs: Any) -> Pin:
        """Pin cid into remote edge cache
        ref: http://docs.ipfs.io/reference/cli/#ipfs-pin-remote-add

        :param cid: cid to pin
        :return: pin object
        :rtype: Pin
        :raises EdgePinException: if pin request fails
        """
        req = self._http.post(
            ESTUARY_API_PIN,
            data={cid: cid, **kwargs},
            headers=self._headers,
        )

        # expected response as json
        response = _enhanced_response(req)
        # data resulting from estuary endpoint
        # ref: https://docs.estuary.tech/Reference/SwaggerUI#/pinning/post_pinning_pins
        return _pin_factory(response)

    def ls(self) -> Iterator[Pin]:
        """Return current remote pin list
        ref: http://docs.ipfs.io/reference/cli/#ipfs-pin-remote-ls

        :param limit: number of remote pins to return
        :return: list of current remote pin list
        :rtype: Sequence[Pin]
        :raises EdgePinException: if pin request fails
        """
        # expected response as json
        response = self._ls_records()
        return map(_pin_factory, response)

    def unpin(self, cid: CID):
        """Remove pin from edge cache service

        :param cid: cid to remove from cache
        :return: None since we don't receive anything from estuary
        :rtype: None
        """
        content = self._content_by_cid(cid)
        pin_id = content.get("id")  # content id is same as pin id
        req = self._http.delete(f"{ESTUARY_API_PIN}/{pin_id}")
        # we don't consume anything since delete is empty response
        _enhanced_response(req)

    def flush(self, limit: int = 0) -> int:
        """Remove all pinned cid from edge cache service

        :param limit: Maximum number of remote pins to remove
        :return: Number of remote pins removed
        :rtype: int
        :raises EdgePinException if an error occurs during request
        """
        response = self._ls_records()
        limit = limit or len(response)
        sliced = response[:limit]

        for pin in sliced:
            pinned = pin.get("pin")
            cid = pinned.get("cid")
            self.unpin(cid)

        return limit
