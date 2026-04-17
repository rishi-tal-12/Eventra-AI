"""
Pydantic models for the Exhibitor Agent.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Input schema expected by the orchestrator."""
    category: str = Field(description="Event category, e.g. 'Music Festival', 'AI', 'Web3'")
    geography: str = Field(description="Target geography, e.g. 'Austin, TX', 'India'")
    audience_size: int = Field(default=1000, description="Expected audience size")
    top_n: int = Field(default=10, description="Number of exhibitors to return")


class ExhibitorRecommendation(BaseModel):
    """A single recommended exhibitor derived from the sample data."""
    name: str = Field(description="Exhibitor / brand / company name")
    category: str = Field(description="Category the exhibitor falls under")
    relevance_score: float = Field(description="Relevance score from 0-1")
    reason: str = Field(description="Short reason why this exhibitor is relevant")
    past_events: List[str] = Field(default_factory=list, description="Past events they were associated with")
    contact_email: Optional[str] = Field(default=None, description="Contact email if available")
    contact_phone: Optional[str] = Field(default=None, description="Contact phone if available")
    website: Optional[str] = Field(default=None, description="Website URL if available")


class RecommendationResponse(BaseModel):
    """Output schema returned by the exhibitor agent."""
    event_category: str
    event_geography: str
    total_found: int
    recommendations: List[ExhibitorRecommendation]
