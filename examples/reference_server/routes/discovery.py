"""
Discovery endpoint for MedScribe Alliance Protocol

This endpoint returns the discovery document with service capabilities,
authentication methods, supported models, and available features.
"""

import os
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from models import (
    DiscoveryResponse,
    ServiceInfo,
    Endpoints,
    AuthenticationConfig,
    OIDCConfig,
    Capabilities,
    ModelConfig,
    ModelFeatures,
    LanguageConfig,
)

router = APIRouter()


@router.get(
    "/.well-known/medscribealliance",
    response_model=DiscoveryResponse,
    status_code=status.HTTP_200_OK,
    summary="Discovery Document",
    description="Returns service capabilities and configuration. MUST be publicly accessible without authentication.",
)
async def get_discovery_document():
    """
    Get the MedScribe Alliance protocol discovery document.
    
    This endpoint:
    - MUST be publicly accessible without authentication
    - Returns service capabilities, models, languages, and endpoints
    - Can be cached for up to 3 hours (Cache-Control header)
    
    TODO: Production implementation should:
    - Load configuration from environment variables or config file
    - Support multiple environments (dev, staging, prod)
    - Include actual OIDC configuration if supported
    - List real models and their capabilities
    - Specify actual supported audio formats and limits
    """
    
    # TODO: Replace with actual base URL from environment
    base_url = os.getenv("API_BASE_URL", "https://api.scribe.example.com")
    
    # TODO: Replace with actual OIDC configuration if supported
    oidc_config = OIDCConfig(
        issuer="https://accounts.example.com/oauth2",
        authorization_endpoint="https://accounts.example.com/oauth2/authorize",
        token_endpoint="https://accounts.example.com/oauth2/token",
        scopes_supported=["openid", "profile"],
    )
    
    discovery = DiscoveryResponse(
        protocol="medscribealliance",
        protocol_version="0.1",
        supported_versions=["0.1"],
        
        service=ServiceInfo(
            name="Mock Medical Scribe Service",
            documentation_url=f"{base_url}/docs",
            support_email=os.getenv("SUPPORT_EMAIL", "support@scribe.example.com"),
        ),
        
        endpoints=Endpoints(
            base_url=f"{base_url}/v1",
            webhooks_url=f"{base_url}/v1/webhooks",
            templates_url=f"{base_url}/v1/templates",
        ),
        
        authentication=AuthenticationConfig(
            supported_methods=["api_key", "oidc"],
            oidc=oidc_config,
        ),
        
        capabilities=Capabilities(
            audio_formats=[
                "audio/webm;codecs=opus",
                "audio/wav",
                "audio/ogg",
                "audio/ogg;codecs=opus",
                "audio/mp4",
                "audio/m4a",
                "audio/mp3",
            ],
            max_chunk_duration_seconds=20,
            upload_methods=["chunked", "single", "stream"],
            webhook_delivery=True,
            client_sdk_delivery=True,
        ),
        
        # TODO: Replace with actual model configurations
        models=[
            ModelConfig(
                id="lite",
                display_name="Lite",
                languages=["en", "hi"],
                max_session_duration_seconds=600,
                response_speed="fast",
                features=ModelFeatures(
                    realtime_transcription=False,
                    speaker_diarization=False,
                    custom_templates=False,
                ),
            ),
            ModelConfig(
                id="pro",
                display_name="Professional",
                languages=["en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa"],
                max_session_duration_seconds=3600,
                response_speed="standard",
                features=ModelFeatures(
                    realtime_transcription=True,
                    speaker_diarization=True,
                    custom_templates=True,
                ),
            ),
        ],
        
        languages=LanguageConfig(
            supported=["en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa"],
            auto_detection=True,
        ),
    )
    
    # Cache the discovery document for 3 hours
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=discovery.model_dump(),
        headers={
            "Cache-Control": "max-age=10800",
        }
    )
