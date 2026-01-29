"""
Pydantic models for MedScribe Alliance Protocol v0.1
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


# ============================================================================
# Discovery Models
# ============================================================================

class ServiceInfo(BaseModel):
    """Service metadata"""
    name: str = Field(..., description="Human-readable service name")
    documentation_url: Optional[str] = Field(None, description="Link to service documentation")
    support_email: Optional[str] = Field(None, description="Support contact email")


class Endpoints(BaseModel):
    """API endpoints configuration"""
    base_url: str = Field(..., description="Base URL for API endpoints")
    webhooks_url: Optional[str] = Field(None, description="Webhook registration endpoint")
    templates_url: Optional[str] = Field(None, description="Templates endpoint URL")


class OIDCConfig(BaseModel):
    """OIDC-specific configuration"""
    issuer: str = Field(..., description="OIDC issuer URL")
    authorization_endpoint: str = Field(..., description="Authorization endpoint")
    token_endpoint: str = Field(..., description="Token endpoint")
    scopes_supported: List[str] = Field(default=["openid", "profile"], description="Supported OAuth scopes")


class AuthenticationConfig(BaseModel):
    """Authentication methods and configuration"""
    supported_methods: List[str] = Field(..., description="Supported auth methods")
    oidc: Optional[OIDCConfig] = Field(None, description="OIDC configuration if supported")


class Capabilities(BaseModel):
    """Service capabilities and limits"""
    audio_formats: List[str] = Field(..., description="Supported audio MIME types")
    max_chunk_duration_seconds: int = Field(..., description="Maximum audio chunk duration")
    upload_methods: List[str] = Field(..., description="Supported upload methods")
    webhook_delivery: bool = Field(True, description="Whether webhook delivery is supported")
    client_sdk_delivery: bool = Field(True, description="Whether client SDK delivery is supported")


class ModelFeatures(BaseModel):
    """Model-specific features"""
    realtime_transcription: bool = Field(False, description="Live transcription during recording")
    speaker_diarization: bool = Field(False, description="Automatic speaker identification")
    custom_templates: bool = Field(False, description="Support for custom template creation")


class ModelConfig(BaseModel):
    """Model configuration and capabilities"""
    id: str = Field(..., description="Unique model identifier")
    display_name: str = Field(..., description="Human-readable name")
    languages: List[str] = Field(..., description="ISO 639-1 language codes supported")
    max_session_duration_seconds: int = Field(..., description="Maximum session length allowed")
    response_speed: Optional[str] = Field("standard", description="Processing speed")
    features: Optional[ModelFeatures] = Field(None, description="Feature availability flags")


class LanguageConfig(BaseModel):
    """Language support configuration"""
    supported: List[str] = Field(..., description="List of supported ISO 639-1 language codes")
    auto_detection: bool = Field(True, description="Whether automatic language detection is supported")


class DiscoveryResponse(BaseModel):
    """Discovery document response"""
    protocol: str = Field(default="medscribealliance", description="Protocol identifier")
    protocol_version: str = Field(default="0.1", description="Current protocol version")
    supported_versions: List[str] = Field(default=["0.1"], description="All supported protocol versions")
    service: ServiceInfo
    endpoints: Endpoints
    authentication: AuthenticationConfig
    capabilities: Capabilities
    models: List[ModelConfig]
    languages: LanguageConfig


# ============================================================================
# Session Models
# ============================================================================

class SessionStatus(str, Enum):
    """Session status enumeration"""
    CREATED = "created"
    INITIALIZED = "initialized"
    RECORDING = "recording"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    EXPIRED = "expired"


class UploadType(str, Enum):
    """Audio upload type enumeration"""
    CHUNKED = "chunked"
    SINGLE = "single"
    STREAM = "stream"


class CommunicationProtocol(str, Enum):
    """Communication protocol enumeration"""
    WEBSOCKET = "websocket"
    HTTP = "http"
    RPC = "rpc"


class ModelType(str, Enum):
    """Model type enumeration"""
    PRO = "pro"
    LITE = "lite"


class CreateSessionRequest(BaseModel):
    """Request model for creating a new session"""
    session_mode: Optional[str] = Field(default="dictation", description="Session mode")
    templates: List[str] = Field(..., max_length=2, description="Template IDs to extract (max 2)")
    model: Optional[ModelType] = Field(default=ModelType.LITE, description="Model ID from discovery")
    language_hint: Optional[List[str]] = Field(None, description="ISO 639-1 language hints")
    transcript_language: Optional[str] = Field(None, description="ISO 639-1 language for transcript")
    upload_type: UploadType = Field(..., description="Audio upload method")
    communication_protocol: CommunicationProtocol = Field(..., description="Communication protocol")
    additional_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Pass-through data")


class CreateSessionResponse(BaseModel):
    """Response model for session creation"""
    session_id: str = Field(..., pattern=r"^ses_[a-zA-Z0-9]+$", description="Unique session identifier")
    status: SessionStatus = Field(..., description="Current session status")
    created_at: datetime = Field(..., description="ISO 8601 creation timestamp")
    expires_at: datetime = Field(..., description="ISO 8601 expiry timestamp")
    upload_url: str = Field(..., description="URL for uploading audio files")


class EndSessionRequest(BaseModel):
    """Request model for ending a session"""
    audio_files_sent: int = Field(..., ge=0, description="Number of audio files sent by client")


class EndSessionResponse(BaseModel):
    """Response model for ending a session"""
    session_id: str = Field(..., pattern=r"^ses_[a-zA-Z0-9]+$")
    status: SessionStatus = Field(..., description="Session status after ending")
    message: str = Field(..., description="Human-readable status message")
    audio_files_received: int = Field(..., ge=0)
    audio_files: List[str] = Field(..., description="List of audio file names received")


class SessionProcessingResponse(BaseModel):
    """Response model for session in processing state"""
    session_id: str = Field(..., pattern=r"^ses_[a-zA-Z0-9]+$")
    status: SessionStatus
    created_at: datetime
    expires_at: datetime
    audio_files_received: int = Field(..., ge=0)
    audio_files: List[str]
    additional_data: Dict[str, Any] = Field(default_factory=dict)
    transcript: Optional[str] = None


class SessionCompletedResponse(BaseModel):
    """Response model for completed session"""
    session_id: str = Field(..., pattern=r"^ses_[a-zA-Z0-9]+$")
    status: SessionStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    model_used: Optional[ModelType] = None
    language_detected: Optional[str] = None
    audio_files_received: int = Field(..., ge=0)
    audio_files: List[str]
    additional_data: Dict[str, Any] = Field(default_factory=dict)
    templates: Dict[str, Any] = Field(default_factory=dict)
    transcript: Optional[str] = None


class SessionPartialResponse(BaseModel):
    """Response model for partially completed session"""
    session_id: str = Field(..., pattern=r"^ses_[a-zA-Z0-9]+$")
    status: SessionStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    model_used: Optional[ModelType] = None
    language_detected: Optional[str] = None
    audio_files_received: int = Field(..., ge=0)
    audio_files_processed: int = Field(..., ge=0)
    audio_files: List[str]
    additional_data: Dict[str, Any] = Field(default_factory=dict)
    templates: Dict[str, Any] = Field(default_factory=dict)
    transcript: Optional[str] = None
    processing_errors: Optional[List[Dict[str, Any]]] = None


class ExpiredSessionResponse(BaseModel):
    """Response model for expired session"""
    session_id: str = Field(..., pattern=r"^ses_[a-zA-Z0-9]+$")
    status: SessionStatus = Field(default=SessionStatus.EXPIRED)
    created_at: datetime
    expired_at: datetime
    message: str
    audio_files_received: int = Field(..., ge=0)
    audio_files: List[str]
    additional_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    templates: Optional[Dict[str, Any]] = Field(default_factory=dict)
    transcript: Optional[str] = None


# ============================================================================
# Template Models
# ============================================================================

class TemplateInfo(BaseModel):
    """Template information for discovery"""
    id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Human-readable template name")
    description: str = Field(..., description="Brief description of template purpose")


class TemplatesListResponse(BaseModel):
    """Response model for templates listing"""
    templates: List[TemplateInfo] = Field(..., description="List of available templates")


# ============================================================================
# Audio Models
# ============================================================================

class AudioUploadResponse(BaseModel):
    """Response model for audio upload"""
    success: bool = Field(..., description="Whether upload was successful")
    filename: str = Field(..., description="Simplified filename stored by server")
    original_filename: str = Field(..., description="Original filename from client")
    size_bytes: int = Field(..., description="Size of uploaded file in bytes")


# ============================================================================
# Error Models
# ============================================================================

class ErrorDetail(BaseModel):
    """Error detail structure"""
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: ErrorDetail
