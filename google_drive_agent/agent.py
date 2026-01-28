import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent

# callbacks
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional
from google.adk.models import LlmResponse, LlmRequest
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.base_tool import BaseTool
from typing import Dict, Any

# tool: appint & auth
from google.adk.tools.application_integration_tool.application_integration_toolset import ApplicationIntegrationToolset
from google.adk.tools.openapi_tool.auth.auth_helpers import dict_to_auth_scheme
from google.adk.auth import AuthCredential
from google.adk.auth import AuthCredentialTypes
from google.adk.auth import OAuth2Auth

# tool: MCP (local)
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

# =============================================
# Tools: Application Integration & Auth
# =============================================
oauth2_data_google_cloud = {
  "type": "oauth2",
  "flows": {
      "authorizationCode": {
          "authorizationUrl": "https://accounts.google.com/o/oauth2/auth",
          "tokenUrl": "https://oauth2.googleapis.com/token",
          "scopes": {
              "https://www.googleapis.com/auth/drive.readonly": "readonly",
              "https://www.googleapis.com/auth/drive.metadata": "metadata readonly",
          },
      }
  },
}

oauth_scheme = dict_to_auth_scheme(oauth2_data_google_cloud)

auth_credential = AuthCredential(
  auth_type=AuthCredentialTypes.OAUTH2,
  oauth2=OAuth2Auth(
      client_id=os.getenv("API_INT_OAUTH_CLIENTID"), #TODO: replace with client_id
      client_secret=os.getenv("API_INT_OAUTH_SECRET"), #TODO: replace with client_secret
  ),
)

connector_tool = ApplicationIntegrationToolset(
   project="crafty-progress-421108", # TODO: replace with GCP project of the connection
   location="europe-west4", #TODO: replace with location of the connection
   connection="google-drive-auth-agents", #TODO: replace with connection name "projects/genai-app-builder/locations/europe-central2/connections/gdrive-connection", ##
   entity_operations={},##{"Entity_One": ["LIST","CREATE"], "Entity_Two": []},#empty list for actions means all operations on the entity are supported.
   actions=["GET_files"], #TODO: replace with actions
   ##service_account_credentials='{...}', # optional
   tool_name_prefix="tool_gdrive",
   tool_instructions="Use this tool to list gdrive files",
   auth_scheme=oauth_scheme,
   auth_credential=auth_credential,
)


# =============================================
# Tools: MCP (local/STDIO)
# =============================================
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")
mcp_filesystem_tool = McpToolset(
    connection_params=StdioConnectionParams(
        server_params = StdioServerParameters(
            command='npx',
            args=[
                "-y",  # Argument for npx to auto-confirm install
                "@modelcontextprotocol/server-filesystem",
                os.path.abspath(TARGET_FOLDER_PATH),
            ],
        ),
    ),
    # Optional: Filter which tools from the MCP server are exposed
    tool_filter=['list_directory']
)


# =============================================
# Callbacks
# =============================================
def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    return

def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    return

def before_model_callback(callback_context: CallbackContext, llm_request: LlmRequest) -> Optional[LlmResponse]:
    return

def after_model_callback(callback_context: CallbackContext, llm_response: LlmResponse) -> Optional[LlmResponse]:
    return

def before_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext) -> Optional[Dict]:
    return

def after_tool_callback(tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict) -> Optional[Dict]:
    return


# =============================================
# Agents
# =============================================
root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description="You are helpful assistant helping users with questions files stored in Google Drive and on the local machine.",
    instruction="""
        Use the availabe tools to answer the user questions and files. 
        - Use tool `connector_tool` for questions around files on Google Drive
        - Use tool `mcp_filesystem_tool` for questions around files on the local machine.

        If the destination of the files is not specified, then list the files of all destinations.
        """,
    tools = [connector_tool, mcp_filesystem_tool],
    before_agent_callback=before_agent_callback,
    before_model_callback=before_model_callback,
    before_tool_callback=before_tool_callback,
    after_agent_callback=after_agent_callback,
    after_model_callback=after_model_callback,
    after_tool_callback=after_tool_callback,
)
