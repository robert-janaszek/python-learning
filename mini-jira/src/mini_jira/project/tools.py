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
        project = next((p for p in projects if p.name == name), None)

        if project is None:
            return "Project was not found"
        
        return project.id

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
