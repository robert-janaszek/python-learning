from openai.types.chat import ChatCompletionToolParam

from mini_jira.project.service import ProjectService

def make_list_projects(project_service: ProjectService):
    async def list_projects() -> list[dict[str, int | str]]:
        projects = await project_service.get_projects()
        return [{ "id": project.id, "name": project.name } for project in projects]

    tool: ChatCompletionToolParam = {
        "type": "function",
        "function": {
            "name": "list_projects",
            "description": "Lists all projects from the database",
        },
    }

    return list_projects, tool

def make_find_project(project_service: ProjectService):
    async def find_project(name: str) -> int | str:
        projects = await project_service.get_projects()
        projects_by_name = [project for project in projects if project.name == name]
        if len(projects_by_name) > 1:
            return "More than one project was found with that name."

        if len(projects_by_name) == 0:
            return "Project was not found"
        
        return projects_by_name[0].id

    tool: ChatCompletionToolParam = {
        "type": "function",
        "function": {
            "name": "find_project",
            "description": (
                "Finds a project by name and returns its id. "
                "Returns an error description when no project has that name, "
                "or when more than one project does."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            },
        },
    }

    return find_project, tool
