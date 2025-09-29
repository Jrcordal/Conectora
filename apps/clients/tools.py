from typing import Dict, List
from langchain_core.tools import tool




@tool
def role_matches(
    user_ids: Dict[str, List[int]],
    candidate_roles: Dict[str, List[str]],
    recommended_roles:List[str]
    )-> List[int]:
    """
    Return the user_ids whose role matches approximately the list of roles in the team recommendation

    Args:
        user_ids (dict): Dictionary of the user ids, containing all ids in int value
        candidate_roles (dict): Dictionary containing the main_developer_role field of all developer profiles, in str value
        recommended_roles (list): List of roles recommended for the project     
    
    Returns:
        list[int]: IDs of users whose roles falls are similar to any recommended role.
    """
    user_ids = user_ids.get("id", [])
    candidate_roles = candidate_roles.get("main_developer_role",[])

    





@tool
def get_experience_in_range(
    min_range: int,
    max_range: int,
    data: Dict[str, List[int]]
) -> List[int]:
    """
    Return the user_ids whose relevant_years_of_experience fall within [min_range, max_range].

    Args:
        min_range (int): Minimum years of experience (inclusive).
        max_range (int): Maximum years of experience (inclusive).
        data (dict): Dictionary with keys:
            - "user_ids": list of user IDs
            - "relevant_years_of_experience": list of years of experience (same order as user_ids)

    Returns:
        list[int]: IDs of users whose experience falls in the range.
    """
    user_ids = data.get("user_ids", [])
    years = data.get("relevant_years_of_experience", [])

    result_ids = [
        uid for uid, exp in zip(user_ids, years)
        if min_range <= exp <= max_range
    ]

    return result_ids


