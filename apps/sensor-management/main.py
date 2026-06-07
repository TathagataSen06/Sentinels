from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uuid
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sentinels Sensor Management API",
    description="Control plane for massive scale sensor fleet management.",
    version="1.0.0"
)

from schemas import EnrollmentRequest, EnrollmentResponse, HeartbeatRequest, HeartbeatResponse, RenewalRequest, RenewalResponse, AssetReportRequest, AssetReportResponse
from services.enrollment import process_enrollment, process_renewal
from services.heartbeat import process_heartbeat

@app.post("/api/v1/sensors/enroll", response_model=EnrollmentResponse)
async def enroll_sensor(request: EnrollmentRequest):
    """
    Enroll a new sensor using a bootstrap token and a CSR.
    Returns a signed client certificate for future mTLS communication.
    """
    try:
        response = await process_enrollment(request)
        return response
    except ValueError as e:
        logger.error(f"Enrollment failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/sensors/renew", response_model=RenewalResponse)
async def renew_sensor(request: RenewalRequest):
    """
    Renew an existing mTLS certificate. The request MUST be authenticated via the old valid mTLS certificate.
    """
    try:
        response = await process_renewal(request)
        return response
    except Exception as e:
        logger.error(f"Renewal failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/sensors/heartbeat", response_model=HeartbeatResponse)
async def sensor_heartbeat(request: HeartbeatRequest):
    """
    Receive heartbeat from a sensor.
    Returns the next expected check-in intervals to support adaptive jitter.
    """
    try:
        response = await process_heartbeat(request)
        return response
    except Exception as e:
        logger.error(f"Heartbeat failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/assets/report", response_model=AssetReportResponse)
async def report_asset(request: AssetReportRequest):
    """
    Track a deceptive asset (canary token) that was deployed by a sensor.
    """
    try:
        # In a real implementation, write to DB to track the asset
        logger.info(f"Tracking deployed asset: {request.asset_type} at {request.asset_path} from sensor {request.sensor_uuid}")
        return AssetReportResponse(status="tracked", asset_id=uuid.uuid4())
    except Exception as e:
        logger.error(f"Asset reporting failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
