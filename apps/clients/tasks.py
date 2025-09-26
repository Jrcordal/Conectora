from celery import shared_task
from django.conf import settings
import boto3
import tempfile
from langchain_community.document_loaders import PyPDFLoader,Docx2txtLoader
from .llms import llm_01_temperature, llm_08_temperature, llm_06_temperature
import os
import tempfile
from .pydantic_models import SoftwareRequirements, StackRecommendation, TeamRequirements
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate


import logging
logger = logging.getLogger(__name__)


def load_doc_from_s3(bucket: str, key: str):
    s3_client = boto3.client("s3")
    fd, tmp_path = tempfile.mkstemp(suffix=os.path.splitext(key)[1])
    os.close(fd)
    s3_client.download_file(bucket, key, tmp_path)

    ext = tmp_path.lower().split(".")[-1]
    if ext == "pdf":
        docs = PyPDFLoader(tmp_path).load()
    elif ext == "docx":
        docs = Docx2txtLoader(tmp_path).load()
    else:
        raise ValueError(f"Unsupported format: {ext}")

    os.remove(tmp_path)
    return "\n\n".join(d.page_content for d in docs)

def structure_requirements(intake_instance):

    # first requirements draft
    instructions_template = """
    You are a software requirements engineer. Use the provided input to make a draft of a software requirements specification.
    The draft should include:
    - The purpose of the system (definitions, system overview, references),
    - The overall description (product perspective, design constraints, product functions, user characteristics),
    - The specific requirements (external interface requirements, functional requirements, performance requirements, logical database requirement, software system attributes),
    - The recommended stack (the client's recommended stack for the software),
    - Other information that might be relevant.

    If you can create more requirements based on the needs, do it.
    If some aspects cannot be filled due to the lack of information, mention it in the draft.
    """
    input_template = """
    Who are you and what do you do?
    {company_description}
    What do you need?
    {need}
    What problem are you trying to solve?
    {problem}
    Who are the end users?
    {end_users}
    What do you hope to achieve with this project as end goal? 
    {end_goal}
    What features do you think the solution must definitely include?
    {must_features}
    Are there any workflows or processes that must remain unchanged? 
    {required_workflows}
    Is there anything that must not be done? 
    {must_not_do}
    Do you have any tech stack in mind for the project?
    {recommended_stack}
    Would you like to share anything else that might be relevant? 
    {other_info}
    Do you have any existing technical documentation, previous proposals, mockups, or wireframes? 
    {existing_docs}
    """

    prompt_for_requirements_draft = PromptTemplate.from_template(
        instructions_template + "\n\nINPUT:\n" + input_template
    )

    bucket = settings.AWS_STORAGE_BUCKET_NAME

    existing_docs = [
        f"==== Document {i+1} ====\n{load_doc_from_s3(bucket, doc.file.name)}\n==== End Document {i+1} ===="
        for i, doc in enumerate(intake_instance.intakedocuments.all())
    ]
    prompt_for_requirements_draft = prompt_for_requirements_draft.format(
        company_description=intake_instance.company_description,
        need=intake_instance.need,
        problem=intake_instance.problem,
        end_users=intake_instance.end_users,
        end_goal=intake_instance.end_goal,
        must_features=intake_instance.must_features,
        required_workflows=intake_instance.required_workflows,
        must_not_do=intake_instance.must_not_do,
        other_info=intake_instance.other_info,
        recommended_stack=intake_instance.recommended_stack,
        existing_docs="\n\n".join(existing_docs),  # separador doble salto de línea
        )


    llm_requirements_structured = llm_01_temperature.with_structured_output(SoftwareRequirements)

    draft_requirements = llm_08_temperature.invoke(prompt_for_requirements_draft)
    draft_requirements_clean = draft_requirements.content 

    # Structure requirements in json with a lighter model for speed.
    prompt_to_structure_requirements = ChatPromptTemplate.from_messages([
    ("system", "You are a software requirements analyst and project manager."),
    ("human", 
    """
    Based on the following draft description, structure it into the fields of a software requirements specification. Use the predefined schema and leave fields empty if no information is found.

    DRAFT:
    {draft_text}
    """)
    ])


    prompt_to_structure_requirements = prompt_to_structure_requirements.format(draft_text=draft_requirements_clean)

    structured_requirements = llm_requirements_structured.invoke(prompt_to_structure_requirements)
    structured_requirements_json = structured_requirements.model_dump_json()

    return structured_requirements_json

def structure_tech_stack(structured_requirements):

    llm_stack_recommendation_structured = llm_08_temperature.with_structured_output(StackRecommendation)
    draft_stack_recommendation_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a software requirements analyst and project manager."),
        ("human", 
        """
    Based on the following software requirements, recommend a stack for the project.

    Software Requirements:
    {software_requirements}
    """)
    ])

    draft_stack_recommendation_prompt = draft_stack_recommendation_prompt.format(software_requirements=structured_requirements)

    stack_recommendation = llm_08_temperature.invoke(draft_stack_recommendation_prompt)

    prompt_structure_stack = ChatPromptTemplate.from_messages([
        ("system", "You are a software requirements analyst and project manager."),
        ("human", 
        """
    Based on the following tech stack description, structure it into the fields of a stack recommendation specification. Use the predefined schema and leave fields empty if no information is found.

    Stack recommendation:
    {stack}
    """)
    ])
    prompt_structure_stack = prompt_structure_stack.format(stack=stack_recommendation.content)

    stack_recommendation_structured = llm_stack_recommendation_structured.invoke(prompt_structure_stack)

    stack_recommendation_structured_json = stack_recommendation_structured.model_dump_json()

    return stack_recommendation_structured_json

def structure_team_profiles(structured_requirements,structured_tech_stack):

    prompt_draft_team_recommendation = ChatPromptTemplate.from_messages([
        ("system", "You are a software requirements analyst and project manager."),
        ("human", 
        """
    Based on the following stack recommendation, recommend a team of profiles (e.g. Senior Fullstack developer, Junior Frontend, Senior AI engineer, medior python developer, etc.), their description, their responsibilities, their seniority (range of years of experience), their rationale and their required tech stack to make the project based on the stack and software requirements. Take into account the size of the project to recommend more or less members of the team.

    Stack Recommendation:
    {stack_recommendation}

    Software Requirements:
    {software_requirements}
    """)
    ])

    prompt_draft_team_recommendation = prompt_draft_team_recommendation.format(stack_recommendation=structured_tech_stack, software_requirements=structured_requirements)

    team_recommendation = llm_06_temperature.invoke(prompt_draft_team_recommendation)

    prompt_strucure_team = ChatPromptTemplate.from_messages([
        ("system", "You are a software requirements analyst and project manager."),
        ("human", 
        """
    Based on the following developer team description, structure it into the fields of a team recommendation specification. Use the predefined schema and leave fields empty if no information is found.

    Team recommendation:
    {team_recommendation}
    """)
    ])
    prompt6_input = prompt_strucure_team.format(team_recommendation=team_recommendation.content)

    llm_team_recommendation_structured = llm_01_temperature.with_structured_output(TeamRequirements)

    team_recommendation_structured = llm_team_recommendation_structured.invoke(prompt6_input)

    team_recommendation_structured_json = team_recommendation_structured.model_dump_json()

    return team_recommendation_structured_json

#def match_candidates(strucured_team):
