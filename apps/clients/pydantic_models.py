
from pydantic import BaseModel, Field
from typing import Optional, List

StrList = Optional[List[str]]


# Software Requirements

class Introduction(BaseModel):
    scope: Optional[str] = Field(None, description="Scope of the system")
    definitions: StrList = Field(None, description="Definitions, acronyms, abbreviations")
    references: StrList = Field(None, description="References and sources")

class NonFunctionalRequirements(BaseModel):
    reliability: StrList = Field(None, description="Reliability requirements")
    availability: StrList = Field(None, description="Availability requirements")
    performance: StrList = Field(None, description="Performance requirements")
    security: StrList = Field(None, description="Security requirements")
    privacy: StrList = Field(None, description="Privacy requirements")
    usability: StrList = Field(None, description="Usability requirements")
    accessibility: StrList = Field(None, description="Accessibility requirements")
    maintainability: StrList = Field(None, description="Maintainability requirements")
    portability: StrList = Field(None, description="Portability requirements")
    compliance: StrList = Field(None, description="Regulatory or standards compliance")

class Purpose(BaseModel):
    objectives: StrList = Field(None, description="Business and product objectives")
    success_criteria: StrList = Field(None, description="Measurable acceptance/success criteria")

class OverallDescription(BaseModel):
    product_perspective: StrList = Field(None, description="System context and positioning")
    product_functions: StrList = Field(None, description="High-level product capabilities")
    user_characteristics: StrList = Field(None, description="User classes, personas, skills")
    design_constraints: StrList = Field(None, description="Standards, tech limits, policies")
    assumptions_dependencies: StrList = Field(None, description="Assumptions and external deps")
    out_of_scope: StrList = Field(None, description="Explicitly excluded features/areas")

class ExternalInterfaces(BaseModel):
    ui: StrList = Field(None, description="User interface requirements")
    api: StrList = Field(None, description="Public/internal API contracts")
    hardware: StrList = Field(None, description="Hardware interfaces")
    communications: StrList = Field(None, description="Network/protocol interfaces")
    other: StrList = Field(None, description="Other interfaces")

class SpecificRequirements(BaseModel):
    functional_requirements: StrList = Field(None, description="Detailed functional 'shall' statements")
    external_interface_requirements: Optional[ExternalInterfaces] = Field(None, description="Detailed external interfaces by type")
    performance_requirements: StrList = Field(None, description="Throughput, latency, SLAs")
    logical_database_requirements: StrList = Field(None, description="Data model, integrity, retention")
    data_migration_requirements: StrList = Field(None, description="Legacy import, mapping, cutover")
    acceptance_criteria: StrList = Field(None, description="Scenario-based acceptance tests")

class SoftwareRequirements(BaseModel):
    introduction: Optional[Introduction] = Field(None, description="Introductory material")
    purpose: Optional[Purpose] = Field(None, description="Objectives and success criteria")
    overall_description: Optional[OverallDescription] = Field(None, description="Context and coarse view")
    non_functional_requirements: Optional[NonFunctionalRequirements] = Field(None, description="Quality attributes")
    specific_requirements: Optional[SpecificRequirements] = Field(None, description="Detailed requirements")
    recommended_stack: StrList = Field(None, description="Client's recommended stack")
    other_info: StrList = Field(None, description="Miscellaneous relevant information")


# Tech Stack

class TechStack(BaseModel):
    frontend: list[str]
    backend: list[str]
    database: list[str]
    infrastructure: list[str]

class StackRecommendation(BaseModel):
    name: str = Field(description="Name or label for the stack option")
    preferred_stack: TechStack = Field(description="Stack selected as most suitable")
    rationale: Optional[str] = Field(description="Reason why this stack is recommended")
    pros: list[str] = Field(description="Pros of the recommended stack")
    cons: list[str] = Field(description="Cons of the recommended stack")
    need_more_info: Optional[bool] = Field(description="Whether more input is needed to decide on a stack")


class TechStack(BaseModel):
    frontend: StrList = Field(None, description="Frontend frameworks and libraries")
    backend: StrList = Field(None, description="Backend frameworks and runtimes")
    database: StrList = Field(None, description="OLTP/OLAP, SQL/NoSQL, search engines")
    mobile: StrList = Field(None, description="Native, cross-platform, or hybrid mobile frameworks")
    api_gateway: StrList = Field(None, description="API gateways, BFF, or GraphQL servers")
    auth_identity: StrList = Field(None, description="Authentication/Authorization, IAM, SSO, OAuth/OIDC")
    caching: StrList = Field(None, description="In-memory caches, CDN edge caching")
    messaging_streams: StrList = Field(None, description="Queues, streams, event buses")
    search: StrList = Field(None, description="Search engines and indexing tools")
    data_analytics: StrList = Field(None, description="ETL/ELT, lakehouse, BI platforms")
    observability: StrList = Field(None, description="Logging, metrics, tracing, alerting")
    testing_quality: StrList = Field(None, description="Testing frameworks and QA tooling")
    devops_ci_cd: StrList = Field(None, description="CI/CD pipelines and Infrastructure-as-Code")
    infrastructure: StrList = Field(None, description="Cloud platforms, container orchestration, edge/CDN")
    security_privacy: StrList = Field(None, description="WAF, secrets management, key management, DLP")
    compliance_tools: StrList = Field(None, description="Audit, evidence collection, GRC tools")

class StackRecommendation(BaseModel):
    name: str = Field(description="Name or label for the recommended option")
    preferred_stack: TechStack
    rationale: StrList = Field(None, description="Reasoning behind this tech stack recommendation")
    pros: List[str] = Field(default_factory=list, description="Advantages of this recommended stack")
    cons: List[str] = Field(default_factory=list, description="Disadvantages of this recommended stack")
    need_more_info: Optional[bool] = Field(False, description="Whether more input is needed to refine the recommendation")



class ExperienceRange(BaseModel):
    min_years: float = Field(description="Minimum years of experience")
    max_years: float = Field(description="Maximum years of experience")

class TeamMember(BaseModel):
    role: str = Field(description="The role of the team member")
    description: str = Field(description="The description of the team member")
    responsibilities: list[str] = Field(description="The responsibilities of the team member")
    seniority: ExperienceRange
    rationale: str = Field(description="The rationale for the team member for the particular role")
    tech_stack: TechStack = Field(description="The tech stack required for the team member")
        
class TeamRequirements(BaseModel):
    project_team: list[TeamMember]
    overview: str = Field(description="General description of the proposed team")
    rationale: str = Field(description="Why this team composition was chosen")
    total_members: int = Field(description="Total number of members in the team")