# Travel Assistant Agent

A practical AI-powered travel planning project that builds personalized itineraries for travelers based on their interests, destination, trip dates, and budget. The project demonstrates how to combine structured Pydantic models, OpenAI chat completions, mocked travel data, and evaluation logic to generate and refine a city trip plan.

This repository is centered around the fictional city of AgentsVille and shows how an LLM-based itinerary agent can reason over weather, interest matching, activity availability, and budget constraints before producing a final recommendation.

## Table of Contents

- [Overview](#overview)
- [Project Goals](#project-goals)
- [Key Features](#key-features)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [How the Agent Works](#how-the-agent-works)
- [Data Model](#data-model)
- [Usage Example](#usage-example)
- [Evaluation and Quality Checks](#evaluation-and-quality-checks)
- [Extending the Project](#extending-the-project)
- [Notes](#notes)

## Overview

The project creates a travel assistant that can:

- ingest traveler information such as names, ages, and interests
- validate the trip constraints with Pydantic models
- review weather and activity schedules for the destination city
- generate an itinerary using a prompt-driven LLM agent
- check whether the suggestions fit the users' interests and budget
- verify that planned activities exist and align with weather conditions
- improve the itinerary through iterative revision and evaluation

In other words, it is a mini end-to-end agent workflow for trip planning using LLMs, structured outputs, and application logic.

## Project Goals

The core goals of this project are to:

1. Demonstrate how to create an AI travel planner using OpenAI-compatible models.
2. Show how to structure inputs and outputs with Pydantic.
3. Model a realistic travel planning pipeline using mocked APIs and data.
4. Teach prompt engineering concepts such as role prompting, task instructions, and schema-driven JSON generation.
5. Introduce evaluation methods that catch budget, weather, or interest mismatches.
6. Illustrate how an agent can revise an itinerary based on feedback and validation results.

## Key Features

- Travel data modeling with `Traveler`, `VacationInfo`, `TravelPlan`, and related schemas
- Interest categorization via `Interest` enums
- OpenAI chat wrapper through `ChatAgent` and `do_chat_completion`
- Mock weather and activity dataset for a specific trip window
- Automated itinerary generation from structured vacation details
- Activity matching against traveler interests
- Cost validation against the trip budget
- Weather compatibility analysis for outdoor vs indoor activities
- Iterative revision loop for itinerary improvement

## Project Structure

```text
TravelAssitantAgent/
├── README.md
├── project_lib.py
├── project_starter.ipynb
└── .gitignore
```

### File overview

- `project_lib.py`
  - Contains reusable library utilities, enums, the `ChatAgent` wrapper, and helper functions for chat completion calls.
  - Also includes the mock activity catalog used by the itinerary generation process.

- `project_starter.ipynb`
  - Main notebook walkthrough for the project.
  - Covers setting up the environment, defining trip data, generating an itinerary, evaluating output, and revising the plan.

- `README.md`
  - Project overview and usage documentation.

## Prerequisites

Before running the project, ensure you have:

- Python 3.10 or newer
- An OpenAI API key or access to an OpenAI-compatible endpoint
- The required Python packages installed
- A notebook environment such as Jupyter Notebook or VS Code with Python support

The notebook includes installation commands for packages like:

- openai
- pandas
- pydantic
- python-dotenv
- json-repair
- numexpr

## Setup

1. Clone the repository.

```bash
git clone https://github.com/priyankodas21-cell/TravelAssitantAgent.git
cd TravelAssitantAgent
```

2. Install dependencies.

```bash
pip install openai pandas pydantic python-dotenv json-repair numexpr
```

3. Configure your environment.

- Create a `.env` file if you are using the environment variable approach.
- Set your API key as `OPENAI_API_KEY`.

Example:

```env
OPENAI_API_KEY=your_api_key_here
```

4. Open the notebook and run the cells in order.

## How the Agent Works

The project follows a clear workflow:

### 1. Define the traveler profile

The notebook defines a `VacationInfo` object containing:

- traveler names and ages
- interests such as tennis, music, art, technology, and more
- destination city
- arrival and departure dates
- trip budget

This structured input gives the LLM a consistent representation of the trip requirements.

### 2. Review mock travel data

The project includes mock weather and activity data for AgentsVille. These data sources act like real APIs but are preloaded for a controlled, reproducible planning environment.

The agent can review:

- weather by date
- event names and descriptions
- price
- related interests
- location and timing

### 3. Generate itinerary with an LLM agent

The `ChatAgent` abstraction wraps the OpenAI API and allows the system to send prompts and receive responses. The itinerary generation step uses a carefully structured system prompt that tells the model to:

- act as an itinerary planning agent
- consider weather and activities
- prioritize user interests
- respect budget and date constraints
- produce a strict output schema

The generated result is validated as a `TravelPlan` object.

### 4. Evaluate itinerary quality

After the itinerary is generated, the project runs validation functions to check for issues such as:

- mismatched dates
- incorrect cost totals
- activities not matching real event data
- insufficient interest alignment
- total cost exceeding budget
- outdoor activities scheduled in poor weather

These checks are important because they improve reliability and help catch hallucinated or low-quality recommendations.

### 5. Revise the itinerary

The notebook introduces a revision agent that uses a ReAct-style loop (Thought → Action → Observation) to improve the itinerary. The agent can:

- inspect activity data
- use a calculator tool
- re-run evaluations
- update the plan based on outcomes
- continue revising until the final result meets the criteria

## Data Model

The project uses Pydantic models to validate input and output structures.

### Main schema objects

- `Interest`
  - Enum of supported interests, including art, reading, technology, music, hiking, tennis, writing, and more.

- `Traveler`
  - Name, age, and list of interests.

- `VacationInfo`
  - Destination, trip dates, travelers, and budget.

- `TravelPlan`
  - City, dates, total cost, and daily itinerary structure.

- `ItineraryDay`
  - Date, weather, and list of recommended activities.

- `ActivityRecommendation`
  - A recommendation object linking an activity to reasons and justification.

These schemas keep the agent output consistent and easier to validate.

## Usage Example

The project is primarily designed to be run in the notebook. A representative flow looks like this:

```python
from openai import OpenAI
from project_lib import ChatAgent

client = OpenAI(api_key="YOUR_API_KEY")

agent = ChatAgent(
    name="ItineraryAgent",
    client=client,
    model="gpt-4.1-mini",
)
```

The notebook then builds a `VacationInfo` instance, creates the itinerary, and validates the result.

The trip is typically generated using a custom system prompt along with the vacation data, then checked through evaluation functions before being delivered as a refined travel plan.

## Evaluation and Quality Checks

The project is designed to go beyond "just generating text." It includes evaluation logic such as:

- `eval_start_end_dates_match`
- `eval_total_cost_is_accurate`
- `eval_total_cost_is_within_budget`
- `eval_itinerary_events_match_actual_events`
- `eval_itinerary_satisfies_interests`
- `eval_activities_and_weather_are_compatible`

These functions help verify the plan is not only creative but also practical and grounded in the available travel data.

## Extending the Project

This repository is a good base for extending into a more production-style travel assistant. Possible next steps include:

- connecting real weather APIs
- integrating a real booking or events API
- adding hotel and airport recommendations
- storing itinerary history in a database
- building a web UI for trip planning
- adding multi-city travel support
- supporting user preferences like accessibility, family travel, or dietary restrictions

## Notes

- The project uses mocked data for reproducibility and experimentation.
- The city is fictional, but the structure is realistic and reusable.
- The notebook is the main instructional artifact; it explains the full thought process behind the itinerary workflow.
- The code is meant to teach agent design patterns rather than be a full production deployment.

## Summary

This project is a compact but complete demonstration of how an AI travel agent can combine structured data, prompt design, API integration, and validation to generate useful trip recommendations. It is especially useful for learning how LLM-based agents work in practice, especially in domains where structured planning, personalization, and factual constraints matter.

If you want to use this project as a learning tool, start with the notebook and work through the itinerary generation and evaluation steps in order. That will give you the clearest understanding of the full planning loop.
