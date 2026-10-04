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