# HubSpot Leads Sync API

A FastAPI application for syncing lead data with HubSpot CRM. Supports batch and single contact creation via REST endpoints.

## Features

- Create and sync individual leads to HubSpot.
- Batch upsert contacts to HubSpot.
- CORS support for local development.

## Requirements

- Python 3.12+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Requests](https://docs.python-requests.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Uvicorn](https://www.uvicorn.org/)
- [Starlette](https://www.starlette.io/)
- [SQLite](https://www.sqlite.org/index.html)

Install dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

Set your HubSpot API credentials in a `.env` file:

```
HUBSPOT_ACCESS_TOKEN=your-access-token
HUBSPOT_BASE_URL=https://api.hubapi.com
```

## Database Setup

The app uses SQLite for storing logs and lead data.

Initialize the database:

```sh
python init_db.py
```

## Usage

Start the API server:

```sh
uvicorn app.main:app --reload --env-file .env
```

### Endpoints

#### Batch Sync Leads

`POST /leads/batch/`

Request body (JSON):

```json
[
  {
    "firstname": "John",
    "lastname": "Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "company": "Acme Inc"
  }
]
```

#### Sync Single Lead

`POST /leads/sync/`

Request body (JSON):

```json
{
  "firstname": "Jane",
  "lastname": "Smith",
  "email": "jane@example.com",
  "phone": "0987654321",
  "company": "Beta LLC"
}
```

## Project Structure

- `main.py`: FastAPI app and endpoints
- `hubspot/api.py`: HubSpot API integration
- `.env`: Environment variables
- `requirements.txt`: Python dependencies

## License

MIT
