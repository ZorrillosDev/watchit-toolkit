import nucleus.core.http as http_client

from dataclasses import dataclass
from nucleus.core.http import Response
from nucleus.core.types import CID, Any, JSON, URL
from nucleus.sdk.exceptions import StorageServiceError

from .types import Pin
from .constants import ESTUARY_API_PIN, ESTUARY_API_PUBLIC


@dataclass
class EstuaryClient:
    """Estuary client implements Service"""

    endpoint: URL
    key: str

    def __post_init__(self):
        self._http = http_client.live_session(self.endpoint)
        self._http.headers.update({"Authorization": f"Bearer {self.key}"})

    def _safe_request(self, res: Response) -> JSON:
        """Amplifier helper method to handle response from Estuary API

        :param res: expected response
        :return: json response
        :rtype: JSON
        :raises StorageServiceError: if an error occurs during request
        """

        # expected response as json
        response = res.json()

        # if response fail
        if not res.ok:
            """
            Observable behavior:
                {
                    "code": 0,
                    "details": "string",
                    "reason": "string"
                }
            """
            error_description = response["error"]["details"]
            raise StorageServiceError(
                f"exception raised during request: {error_description}"
            )

        return response

    def _content_by_cid(self, cid: CID) -> JSON:
        """Collect details from estuary based on CID
        ref: https://docs.estuary.tech/Reference/SwaggerUI#/public/get_public_by_cid__cid_

        :param cid: cid to retrieve content details
        :return: cid content details
        :rtype: JSON
        :raises EdgePinException: if pin request fails
        """

        content_uri = f"{ESTUARY_API_PUBLIC}/by-cid/{cid}"
        req = self._http.get(content_uri)

        # expected response as json
        response = self._safe_request(req)
        return response.get("content", {})

    def pin(self, cid: CID, **kwargs: Any) -> Pin:
        """Pin cid into estuary

        :param cid: cid to pin
        :return: pin object
        :rtype: JSON
        :raises StorageServiceError: if pin request fails
        """
        # ref:
        # https://docs.estuary.tech/Reference/SwaggerUI#/pinning/post_pinning_pins
        req = self._http.post(ESTUARY_API_PIN, data={cid: cid, **kwargs})
        json_response = self._safe_request(req)

        return Pin(
            cid=json_response["cid"],
            name=json_response["name"],
            status="pending",
        )

    def unpin(self, cid: CID) -> CID:
        """Remove pin from estuary

        :param cid: cid to remove from cache
        :return: just removed CID
        :rtype: CID
        :raises StorageServiceError: if an error occurs during request
        """
        # content id is same as pin id
        pin_id = self._content_by_cid(cid).get("id")
        response = self._http.delete(f"{ESTUARY_API_PIN}/{pin_id}")
        # If error happens then raise standard exception.
        self._safe_request(response)
        return cid


__all__ = ["EstuaryClient"]
