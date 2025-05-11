from __future__ import annotations

import os

import aiohttp

from wizzpert import api, rtc
from wizzpert.agents import (
    DEFAULT_API_CONNECT_OPTIONS,
    NOT_GIVEN,
    AgentSession,
    APIConnectOptions,
    NotGivenOr,
    utils,
)
from wizzpert.agents.voice.avatar import DataStreamAudioOutput
from wizzpert.agents.voice.room_io import ATTRIBUTE_PUBLISH_ON_BEHALF

from .api import TavusAPI, TavusException
from .log import logger

SAMPLE_RATE = 24000
_AVATAR_AGENT_IDENTITY = "tavus-avatar-agent"
_AVATAR_AGENT_NAME = "tavus-avatar-agent"


class AvatarSession:
    """A Tavus avatar session"""

    def __init__(
        self,
        *,
        replica_id: NotGivenOr[str] = NOT_GIVEN,
        persona_id: NotGivenOr[str] = NOT_GIVEN,
        api_url: NotGivenOr[str] = NOT_GIVEN,
        api_key: NotGivenOr[str] = NOT_GIVEN,
        avatar_participant_identity: NotGivenOr[str] = NOT_GIVEN,
        avatar_participant_name: NotGivenOr[str] = NOT_GIVEN,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> None:
        self._http_session: aiohttp.ClientSession | None = None
        self._conn_options = conn_options

        self._persona_id = persona_id
        self._replica_id = replica_id
        self._api = TavusAPI(
            api_url=api_url,
            api_key=api_key,
            conn_options=conn_options,
            session=self._ensure_http_session(),
        )

        self._avatar_participant_identity = avatar_participant_identity or _AVATAR_AGENT_IDENTITY
        self._avatar_participant_name = avatar_participant_name or _AVATAR_AGENT_NAME

    def _ensure_http_session(self) -> aiohttp.ClientSession:
        if self._http_session is None:
            self._http_session = utils.http_context.http_session()

        return self._http_session

    async def start(
        self,
        agent_session: AgentSession,
        room: rtc.Room,
        *,
        wizzpert_url: NotGivenOr[str] = NOT_GIVEN,
        wizzpert_api_key: NotGivenOr[str] = NOT_GIVEN,
        wizzpert_api_secret: NotGivenOr[str] = NOT_GIVEN,
    ) -> None:
        wizzpert_url = wizzpert_url or os.getenv("wizzpert_URL")
        wizzpert_api_key = wizzpert_api_key or os.getenv("wizzpert_API_KEY")
        wizzpert_api_secret = wizzpert_api_secret or os.getenv("wizzpert_API_SECRET")
        if not wizzpert_url or not wizzpert_api_key or not wizzpert_api_secret:
            raise TavusException(
                "wizzpert_url, wizzpert_api_key, and wizzpert_api_secret must be set "
                "by arguments or environment variables"
            )

        wizzpert_token = (
            api.AccessToken(api_key=wizzpert_api_key, api_secret=wizzpert_api_secret)
            .with_kind("agent")
            .with_identity(self._avatar_participant_identity)
            .with_name(self._avatar_participant_name)
            .with_grants(api.VideoGrants(room_join=True, room=room.name))
            # allow the avatar agent to publish audio and video on behalf of your local agent
            .with_attributes({ATTRIBUTE_PUBLISH_ON_BEHALF: room.local_participant.identity})
            .to_jwt()
        )

        logger.debug("starting avatar session")
        await self._api.create_conversation(
            persona_id=self._persona_id,
            replica_id=self._replica_id,
            properties={"wizzpert_ws_url": wizzpert_url, "wizzpert_room_token": wizzpert_token},
        )

        logger.debug("waiting for avatar agent to join the room")
        await utils.wait_for_participant(room=room, identity=self._avatar_participant_identity)

        agent_session.output.audio = DataStreamAudioOutput(
            room=room,
            destination_identity=self._avatar_participant_identity,
            sample_rate=SAMPLE_RATE,
        )
