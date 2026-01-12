# Mock ML Server

Simple Flask server for testing the self-learning ML system.

## Installation

```bash
pip install flask
```

## Usage

```bash
# Start server
python ml_server_mock/mock_server.py

# Server running on http://localhost:8000
```

## Configure Framework

```bash
# Point framework to mock server
observe config set ml.upload_endpoint http://localhost:8000/v1/ml/samples
observe config set ml.contribute true
```

## Test Data Upload

```bash
# Use framework normally - it will upload to mock server
observe project fullcycle --android-source ./app/src --output ./tests/

# Check stats
curl http://localhost:8000/v1/ml/samples/stats
```

## Test Model Updates

```bash
# Check for updates
observe ml check-updates

# Download update
observe ml update-model
```

## Endpoints

- `POST /v1/ml/samples` - Upload training batch
- `GET /v1/ml/samples/stats` - Get upload statistics
- `GET /v1/ml/models/latest` - Get latest model metadata
- `GET /models/download/<version>` - Download model file
- `POST /v1/ml/feedback` - Upload user correction
- `GET /v1/ml/feedback/stats` - Get feedback statistics
- `GET /health` - Health check

## Example Responses

### Upload Stats

```json
{
  "total_batches": 3,
  "total_samples": 3000,
  "platform_distribution": {
    "android": 2400,
    "ios": 600
  },
  "last_upload": "2026-01-12T14:30:00Z"
}
```

### Latest Model

```json
{
  "version": "1.3.0",
  "release_date": "2026-01-12",
  "size_mb": 9.2,
  "accuracy": 0.95,
  "download_url": "http://localhost:8000/models/download/1.3.0",
  "sha256": "def456...",
  "changelog": "• Added 10K new samples..."
}
```
