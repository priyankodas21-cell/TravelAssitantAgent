"""FastAPI endpoints exposing the AgentsVille itinerary agents to concurrent users.

All domain models (VacationInfo, TravelPlan, ...) and agent classes
(ItineraryAgent, ItineraryRevisionAgent) live in project_lib.py -- the single
source of truth also used by the notebook. This module only wires them up to
HTTP endpoints with request-scoped dependency injection:

- Singletons (the read-only AgentsVilleContext and the stateless OpenAI
  client) are built once at startup and injected via Depends.
- Each request builds its own VacationInfo/ItineraryAgent/ItineraryRevisionAgent
  instance, so concurrent users never share conversational state.
- The blocking OpenAI calls run in a worker thread via asyncio.to_thread so
  one slow LLM call cannot block the event loop for other requests.
"""

from __future__ import annotations

import asyncio
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

from project_lib import (
    AgentsVilleContext,
    DEFAULT_CONTEXT,
    ItineraryAgent,
    ItineraryRevisionAgent,
    READ_ONLY_MODEL_DEFAULT,
    REASONING_MODEL_DEFAULT,
    TravelPlan,
    VacationInfo,
)

app = FastAPI(title="AgentsVille Trip Planner API")


@app.on_event("startup")
def _init_singletons() -> None:
    """Builds the process-wide, read-only singletons once at startup.

    Both are safe to share across concurrent requests: the context is frozen/
    immutable, and the OpenAI client holds no per-conversation state of its own.
    """
    app.state.context = DEFAULT_CONTEXT
    app.state.openai_client = OpenAI()


def get_context() -> AgentsVilleContext:
    """Dependency returning the shared, read-only AgentsVilleContext singleton."""
    return app.state.context


def get_openai_client() -> OpenAI:
    """Dependency returning the shared, stateless OpenAI client singleton."""
    return app.state.openai_client


class PlanTripRequest(BaseModel):
    vacation_info: VacationInfo
    model: Optional[str] = Field(default=None)


class ReviseTripRequest(BaseModel):
    vacation_info: VacationInfo
    travel_plan: TravelPlan
    model: Optional[str] = Field(default=None)


@app.post("/itinerary", response_model=TravelPlan)
async def plan_trip(
    request: PlanTripRequest,
    context: AgentsVilleContext = Depends(get_context),
    client: OpenAI = Depends(get_openai_client),
) -> TravelPlan:
    """Generates a fresh itinerary for this request's vacation_info.

    A brand-new ItineraryAgent is created for this call only; nothing about it
    is cached, so this endpoint is safe to call concurrently by many users.
    """
    agent = ItineraryAgent(
        vacation_info=request.vacation_info,
        context=context,
        client=client,
        # Privilege separation: this agent has no tools, so it is restricted to the
        # cheaper read-only model unless the caller explicitly overrides it.
        model=request.model or READ_ONLY_MODEL_DEFAULT,
    )
    try:
        # Run the blocking OpenAI call in a worker thread so this request
        # cannot block the event loop and starve other concurrent requests.
        return await asyncio.to_thread(agent.get_itinerary)
    except Exception as exc:  # noqa: BLE001 - convert to a client-safe HTTP error
        raise HTTPException(status_code=502, detail=f"Failed to generate itinerary: {exc}") from exc


@app.post("/itinerary/revise", response_model=TravelPlan)
async def revise_trip(
    request: ReviseTripRequest,
    context: AgentsVilleContext = Depends(get_context),
    client: OpenAI = Depends(get_openai_client),
) -> TravelPlan:
    """Revises an existing itinerary for this request's vacation_info.

    A brand-new ItineraryRevisionAgent is created for this call only.
    """
    agent = ItineraryRevisionAgent(
        vacation_info=request.vacation_info,
        context=context,
        client=client,
        # Privilege separation: only this tool-calling agent uses the reasoning model.
        model=request.model or REASONING_MODEL_DEFAULT,
    )
    try:
        return await asyncio.to_thread(agent.run_react_cycle, request.travel_plan)
    except Exception as exc:  # noqa: BLE001 - convert to a client-safe HTTP error
        raise HTTPException(status_code=502, detail=f"Failed to revise itinerary: {exc}") from exc
