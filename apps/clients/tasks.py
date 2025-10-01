from celery import shared_task
from django.conf import settings
import boto3
import tempfile
from langchain_community.document_loaders import PyPDFLoader,Docx2txtLoader
from apps.developers.models import DeveloperProfile
from .llms import llm_01_temperature, llm_08_temperature, llm_06_temperature
import os
import tempfile
from .pydantic_models import SoftwareRequirements, StackRecommendation, TeamRecommendation, TemporaryCandidateRoleMatching, SelectedCandidate
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate
from django.forms.models import model_to_dict
import logging
import json
from django.core.serializers.json import DjangoJSONEncoder
from typing import Dict, List
import asyncio
from .models import Intake, Project
from django.utils import timezone


logger = logging.getLogger(__name__)




def structure_requirements(intake_instance):

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
    {client_description}
    What problem are you trying to solve?
    {problem}
    Who are the end users?
    {end_user}
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
        client_description=intake_instance.client_description,
        problem=intake_instance.problem,
        end_user=intake_instance.end_user,
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

    return structured_requirements  # Pydantic object

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


    return stack_recommendation_structured # Pydantic object

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
    prompt_strucure_team = prompt_strucure_team.format(team_recommendation=team_recommendation.content)

    llm_team_recommendation_structured = llm_01_temperature.with_structured_output(TeamRecommendation)

    team_recommendation_structured = llm_team_recommendation_structured.invoke(prompt_strucure_team)


    return team_recommendation_structured #Pydantic object

def match_candidates(structured_team) -> Dict[str, List[int]]:


    def alpha_version_role_matching(all_freelancers_open_to_work, structured_team):
        # This function will be deprecated as it does not scale
        def serialize_freelancers(all_freelancers_open_to_work):
            import json

            """
            Convierte un queryset o lista de objetos de freelancer en un JSON
            con los campos que le interesan al prompt.
            """
            data = []
            for f in all_freelancers_open_to_work:
                data.append({
                    "user_id": f.user_id,
                    "main_developer_role": f.main_developer_role,
                })
            return json.dumps(data, indent=2, ensure_ascii=False)
        #####
        structured_team_json = structured_team(json.dumps(structured_team.model_dump(), indent=2, ensure_ascii=False))
        candidates_dictionary = serialize_freelancers(all_freelancers_open_to_work)
        prompt_role_matching = ChatPromptTemplate.from_messages([
            ("system", "You are a software requirements analyst and project manager."),
            ("human", 
            """
        Based on the team profiles recommendation and the candidates dictionary, generate a json with the user_ids and main_developer_role values that match approximately the role being asked.
        - Consider synonyms/abbreviations (backend engineer ≈ backend, ML Engineer/Data Scientist ≈ data scientist).
        - Ignore seniority markers (jr/sr), 'dev', 'developer', 'engineer'.
        - If a candidate mentions multiple roles, pick the closest among the required roles.
        - 'recommended_role' MUST BE EXACTLY one of the required roles provided.
        - If none is a reasonable match, EXCLUDE the candidate (do not include it in 'matches').
        Schema:
        {
        "matches":[
            {"user_id": int, "main_developer_role": str, "recommended_role": str}
        ]
        }
        
        Team Profiles Recommendation (allowed values for 'recommended_role'):
        {structured_team_input}

        Candidates Dictionary (list of {{user_id, main_developer_role}}):
        {candidates_dictionary_input}
        """)
        ])
        prompt_role_matching = prompt_role_matching.format(candidates_dictionary_input=candidates_dictionary,structured_team_input=structured_team_json)
        llm_temporary_matching_roles = llm_01_temperature.with_structured_output(TemporaryCandidateRoleMatching)

        return llm_temporary_matching_roles.invoke(prompt_role_matching)  # Pydantic object


    
    all_freelancers_open_to_work = (
        DeveloperProfile.objects
        .filter(is_open_to_work=True)
        .only("user_id", "main_developer_role")
    )
    matched: TemporaryCandidateRoleMatching = alpha_version_role_matching(
        all_freelancers_open_to_work,
        structured_team
    )

    unique_required_roles = list({m.role for m in structured_team.project_team})

    matches_by_role: Dict[str, List[int]] = {role: [] for role in unique_required_roles}
    for cand in matched.matches:
        if cand.recommended_role in matches_by_role:
            matches_by_role[cand.recommended_role].append(cand.user_id)




    # Deduplicado por rol preservando orden (higiene, sin perder multirole)
    for role, uids in matches_by_role.items():
        seen = set()
        ordered = []
        for uid in uids:
            if uid not in seen:
                seen.add(uid)
                ordered.append(uid)
        matches_by_role[role] = ordered

    return matches_by_role
# Campos que no queremos serializar porque no son relevantes o son pesados/sensibles
EXCLUDE_FIELDS = [
    "consent_promotional_use",
    "consent_given_at",
    "is_open_to_work",
    "is_open_to_teach",
    "has_cv",
    "cv_file",
    "cv_raw_text",
]



def build_candidates_json_per_role(matches_by_role):
    """
    Crea un JSON por cada rol con la información de todos los candidatos.
    Devuelve {role: json_string}.
    """
    # 1) Recolectar TODOS los user_ids de todos los roles
    all_user_ids_open_to_work = [uid for uids in matches_by_role.values() for uid in uids]

    if not all_user_ids_open_to_work:
        # Si no hay candidatos, devolvemos un JSON vacío por cada rol
        logger.info("No candidates")
        return {} 
    # 2) Traer de la base de datos TODOS los perfiles de una sola vez

    qs = (
        DeveloperProfile.objects
        .filter(user_id__in=all_user_ids_open_to_work)
        .select_related("user")  # trae también la info del usuario (JOIN)
    )
    # 3) Crear un diccionario en memoria {user_id: DeveloperProfile}
    by_user_id = {dp.user_id: dp for dp in qs}

    # ----------------------------------------------------------------------
    # 4) Construir la salida por rol
    # ----------------------------------------------------------------------
    # Para cada rol, vamos a crear un JSON con todos los candidatos asignados a ese rol.
    candidate_lists_per_role_json: Dict[str, str] = {}
    for role, user_ids in matches_by_role.items():
        candidates = []
        for uid in user_ids:
            dp = by_user_id.get(uid)  # aquí recuperamos el objeto en memoria, no query
            if not dp:
                continue

            # Convertimos el modelo en dict, excluyendo campos no importantes
            item = model_to_dict(dp, exclude=EXCLUDE_FIELDS)

            # Añadimos datos básicos del usuario (User asociado al perfil)
            if hasattr(dp, "user"):
                item["user"] = {
                    "id": dp.user_id,
                }

            candidates.append(item)

        # Dumpeamos la lista de candidatos a JSON string (uno por rol)
        candidate_lists_per_role_json[role] = json.dumps(candidates, cls=DjangoJSONEncoder, ensure_ascii=False, indent=2)
        
    return candidate_lists_per_role_json

# 1) Define el prompt UNA VEZ y reúsalo
SELECT_CANDIDATES_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a software requirements analyst and project manager."),
    ("human",
     """
Based on the following software requirements, tech stack, team profiles recommendation,
candidates recommendation for the {role} role and curriculums vitae of the candidates,
select the best candidate for the {role} role.

You can leave some roles empty if you think that the candidates are not suitable for the role.

Software Requirements:
{software_requirements}

Tech Stack:
{tech_stack}

Team Profiles Recommendation:
{structured_team}

Candidates Recommendation for Role {role}:
{candidates_json}
""")
])

# 2) Prepara la chain estructurada una vez
chain_select_candidate = SELECT_CANDIDATES_PROMPT | llm_06_temperature.with_structured_output(SelectedCandidate)


def alpha_select_candidates_sync(roles_dict: dict, sw, stack, team) -> dict:
    def _to_json_str(x) -> str:
        # acepta Pydantic, dict, str
        try:

            if hasattr(x, "model_dump"):
                return json.dumps(x.model_dump(), ensure_ascii=False, indent=2)
            if isinstance(x, (dict, list)):
                return json.dumps(x, ensure_ascii=False, indent=2)
            if isinstance(x, str):
                return x
        except Exception:
            pass
        # último recurso: str(x)
        return str(x)
    """
    roles_dict: {role: '<json string de candidatos>'}  (lo que devuelve build_candidates_json_per_role)
    sw/stack/team: Pydantic o str; se normalizan a JSON string.
    """

    sw_str    = _to_json_str(sw)
    stack_str = _to_json_str(stack)
    team_str  = _to_json_str(team)

    async def alpha_select_candidate(role, sw_req, stack, team, cand_json):
        return await chain_select_candidate.ainvoke({
            "role": role,
            "software_requirements": sw_req,
            "tech_stack": stack,
            "structured_team": team,
            "candidates_json": cand_json,
        })

    async def alpha_run_parallel_unbounded(roles_dict, sw_txt, stack_txt, team_txt):
        coros = [
            alpha_select_candidate(role, sw_txt, stack_txt, team_txt, cand_json)
            for role, cand_json in roles_dict.items()
        ]
        outs = await asyncio.gather(*coros)
        return dict(zip(roles_dict.keys(), outs))

    return asyncio.run(alpha_run_parallel_unbounded(roles_dict, sw_str, stack_str, team_str))





PROGRESS_BY_STATUS = {
    "intake_requirements": 0,
    "proposal_draft": 20,
    "tech_stack_draft": 40,
    "team_recommendation": 60,
    "potential_candidates": 80,
    "selected_candidates": 100,
}


def set_matching_status(project: Project, stage: str, *, progress: int | None = None, extra: dict | None = None):
    project.matching_status = stage
    project.matching_status_changed_at = timezone.now()
    project.processing_progress = progress if progress is not None else PROGRESS_BY_STATUS.get(stage, project.processing_progress)
    update_fields = ["matching_status", "matching_status_changed_at", "processing_progress", "updated_at"]
    if extra:
        for k, v in extra.items():
            setattr(project, k, v)
        update_fields += list(extra.keys())
    project.save(update_fields=update_fields)

@shared_task
def matching_pipeline(intake_id: int, project_id: int):
    intake = Intake.objects.get(pk=intake_id)
    project = Project.objects.get(pk=project_id)
    logger.info(f"Matching pipeline started for project {project_id}, intake {intake_id}")


    # 1) Requirements
    set_matching_status(project, "intake_requirements", progress=10)
    structured_req = structure_requirements(intake)
    set_matching_status(
        project, "proposal_draft", progress=25,
        extra={"proposal_draft": structured_req.model_dump(mode="json")}
    )
    logger.info(f"Requirements structured for project {project_id}")

    # 2) Tech stack

    structured_stack = structure_tech_stack(
        json.dumps(structured_req.model_dump(mode="json"), ensure_ascii=False, indent=2)
    )
    set_matching_status(
        project, "tech_stack_draft", progress=45,
        extra={"tech_stack_draft": structured_stack.model_dump(mode="json")}
    )
    logger.info(f"Tech stack structured for project {project_id}")
    # 3) Team recommendation 
    team_rec = structure_team_profiles(
        json.dumps(structured_req.model_dump(mode="json"), ensure_ascii=False, indent=2),
        json.dumps(structured_stack.model_dump(mode="json"), ensure_ascii=False, indent=2)
    )
    logger.info(f"Team recommendation structured for project {project_id}")
    set_matching_status(
        project, "team_recommendation", progress=60,
        extra={"team_recommendation": team_rec.model_dump(mode="json")}
    )
    logger.info(f"Potential candidates structured for project {project_id}")


    # 4) Potenciales candidatos
    matches_by_role = match_candidates(team_rec)
    # build_candidates_json_per_role espera un dict {role: [user_ids]}
    role_json_map = build_candidates_json_per_role(matches_by_role)  # {role: '<json str>'}
    potential = {r: json.loads(s) for r, s in role_json_map.items()}
    set_matching_status(
        project, "potential_candidates", progress=80,
        extra={"potential_candidates_per_role": potential}
    )
    logger.info(f"Selected candidates structured for project {project_id}")

    # 5) Selección final
    selected_by_role = alpha_select_candidates_sync(
        roles_dict=role_json_map,
        sw=structured_req,
        stack=structured_stack,
        team=team_rec,
    )
    selected_by_role_json = {
        role: (obj.model_dump() if hasattr(obj, "model_dump") else obj)
        for role, obj in selected_by_role.items()
    }
    set_matching_status(
        project, "selected_candidates", progress=100,
        extra={"selected_candidates": selected_by_role_json, "status": "presale"}
    )
    print("selected_by_role", selected_by_role)
    return {"selected_by_role": selected_by_role}






# Limitar concurrencia:
"""
async def run_parallel_bounded(roles_dict, sw, stack, team, max_concurrency=6):
    sem = asyncio.Semaphore(max_concurrency)

    async def _one(role, cand_json):
        async with sem:
            return role, await alpha_select_candidate(role, sw, stack, team, cand_json)

    tasks = [asyncio.create_task(_one(role, cj)) for role, cj in roles_dict.items()]
    pairs = await asyncio.gather(*tasks)
    return {role: out for role, out in pairs}
"""