# EcoVision
## Intelligent Environmental Quality Mapping and Prediction Platform

EcoVision is an environmental monitoring and analysis platform
that integrates eight environmental factors:

1. Air Quality
2. Water Quality
3. Green Coverage
4. Waste Management
5. Noise Pollution
6. Traffic Congestion
7. Industrial Activity
8. Climate Conditions

## Technology Stack

- Frontend: React.js
- Backend: Python FastAPI
- Database: SQLite
- Maps: Leaflet
- Assistant: data-grounded EcoVision AI with a deterministic fallback and optional backend-only LLM provider

## Project Structure

- frontend – React application
- backend – FastAPI application
- database – Database files
- docs – Project documentation
- assets – Images and resources

## Run locally

### Backend

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

The frontend expects the FastAPI service at `http://127.0.0.1:8000`.

### Optional dynamic AI provider

The chatbot works without an external provider: it uses the selected location,
recent conversation history, imported environmental records, public connectors,
and environmental explanations. To enable natural-language generation, configure
an OpenAI-compatible provider **only in the backend environment**:

```powershell
$env:ECOVISION_LLM_URL="https://your-provider.example/v1/chat/completions"
$env:ECOVISION_LLM_API_KEY="your-server-side-key"
$env:ECOVISION_LLM_MODEL="your-model-name"
```

The key is never sent to the frontend. The backend sends the provider only
location context and retrieved data; it must not invent measurements, sources,
dates, units, or accuracy. If the provider is unavailable, EcoVision
automatically returns its local data-grounded response instead.

## College Demo Mode

Import the supplied bundle into the separate synthetic-demo tables:

```powershell
cd backend
python .\scripts\import_demo_dataset.py C:\path\to\ecovision_college_demo_dataset.zip
```

In the application sidebar, choose **Enable Demo Mode**. Demo Mode reads only
records marked `data_status=synthetic_demo`; it never combines them with CPCB,
NWDP, FSI, Open-Meteo, or other verified records. Disable Demo Mode to return
to the production integrations.

## Data transparency

Air Quality and Water Quality use the project's imported CPCB/NWDP records.
Green Coverage uses the Esri India Forest Survey 2023 feature service, and
Climate Conditions use Open-Meteo model conditions. Waste Management uses the
official CPCB/data.gov.in 2020–21 source when that source is accessible.
Noise Pollution, Traffic Congestion, and Industrial Activity remain explicitly
unavailable when verified source records are not connected. EcoVision never
fills unavailable locations with fabricated measurements.