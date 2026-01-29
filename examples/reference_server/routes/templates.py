"""
Templates endpoint for MedScribe Alliance Protocol

Endpoints:
- GET /templates - List available templates
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from models import TemplatesListResponse, TemplateInfo, ErrorResponse

router = APIRouter()


@router.get(
    "/templates",
    response_model=TemplatesListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Templates",
    description="Returns templates available to the authenticated user/EMR",
)
async def list_templates():
    """
    List all available templates for the authenticated user/business.
    
    Returns:
        List of templates with ID, name, and description
    
    Note:
        The templates endpoint is behind authentication and returns only
        templates available to the authenticated EMR or user, which may include:
        - Standard templates available to all
        - Custom templates created by the EMR
        - User-specific templates (in B2C model)
    
    TODO: Production implementation should:
    - Validate authentication (API key or OIDC token)
    - Query templates from database based on user/EMR permissions
    - Filter templates by user's subscription tier
    - Return custom templates created by the EMR
    - Include template version information
    - Cache template list with appropriate TTL
    - Support pagination for large template lists
    - Include template schema/structure information
    - Support filtering by category or type
    """
    
    # TODO: Add authentication validation
    # TODO: Extract user ID or business ID from auth token
    # TODO: Query available templates from database
    # TODO: Filter by user permissions and subscription
    
    # Mock template data
    templates = [
        TemplateInfo(
            id="soap",
            name="SOAP Note",
            description="Standard Subjective, Objective, Assessment, Plan format for clinical documentation",
        ),
        TemplateInfo(
            id="medications",
            name="Medications List",
            description="Structured list of prescribed medications with dosage, frequency, and duration",
        ),
        TemplateInfo(
            id="discharge_summary",
            name="Discharge Summary",
            description="Comprehensive discharge documentation including admission details, hospital course, and follow-up",
        ),
        TemplateInfo(
            id="progress_note",
            name="Progress Note",
            description="Daily progress notes documenting patient condition and treatment plan updates",
        ),
        TemplateInfo(
            id="consultation_note",
            name="Consultation Note",
            description="Specialist consultation documentation with recommendations and findings",
        ),
        TemplateInfo(
            id="operative_note",
            name="Operative Note",
            description="Surgical procedure documentation including pre-op, intra-op, and post-op details",
        ),
        TemplateInfo(
            id="history_physical",
            name="History & Physical",
            description="Comprehensive patient history and physical examination findings",
        ),
        TemplateInfo(
            id="lab_results",
            name="Lab Results",
            description="Structured laboratory test results with values and reference ranges",
        ),
        TemplateInfo(
            id="radiology_report",
            name="Radiology Report",
            description="Imaging study findings and radiologist interpretations",
        ),
        TemplateInfo(
            id="vitals",
            name="Vital Signs",
            description="Patient vital signs including blood pressure, heart rate, temperature, and oxygen saturation",
        ),
    ]
    
    return TemplatesListResponse(templates=templates)
