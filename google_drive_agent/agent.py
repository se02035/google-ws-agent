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
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, StreamableHTTPConnectionParams
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
   project=os.getenv("GOOGLE_CLOUD_PROJECT"), # TODO: replace with GCP project of the connection
   location=os.getenv("GOOGLE_CLOUD_LOCATION"), #TODO: replace with location of the connection
   connection="google-drive-auth-agents", #TODO: replace with connection name "projects/genai-app-builder/locations/europe-central2/connections/gdrive-connection", ##
   entity_operations={},##{"Entity_One": ["LIST","CREATE"], "Entity_Two": []},#empty list for actions means all operations on the entity are supported.
   actions=["GET_files"], #TODO: replace with actions
   ##service_account_credentials='{...}', # optional
   tool_name_prefix="tool_gdrive",
   tool_instructions="Use this tool to list Google Drive files",
   auth_scheme=oauth_scheme,
   auth_credential=auth_credential,
)

# =============================================
# Tools: MCP (running locally)
# =============================================

# 1. 3rd party MCP server
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

# # 2. Custom web server (remote/localhost) - currency exchange
MCP_SERVER_URL_CURRENCY_CONVERTER = f"http://{os.getenv("MCP_SERVER_URL_CURRENCY_HOST")}:{os.getenv("MCP_SERVER_CURRENCY_CONVERTER_PORT")}/mcp"
mcp_currency_conversion = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL_CURRENCY_CONVERTER
    )
)

# 3. Custom web server (remote/localhost) - using Gemini CLI
mcp_geminicli_tool = McpToolset(
    connection_params=StdioConnectionParams(
        server_params = StdioServerParameters(
            command='python',
            args=[
                "/home/user/dev/google-ws-agent/tools/gemini_cli_mcp/main.py"
            ],
        ),
        timeout=60,
        env=os.environ
    ),
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
    model=os.getenv("MODEL_NAME"),
    name='adk_cerberus_agent',
    description="You are helpful assistant using different tools to help users",
    instruction="""
        Use the availabe tools to answer the user questions. 
        - For questions around Google Drive files: Use tool `connector_tool`
        - For questions around local files:Use tool `mcp_filesystem_tool`.
        - For questions around running a Gemini CLI command: Use tool `mcp_geminicli_tool`.
        - For questions around currency conversion: Use tool `mcp_currency_conversion`.
        """,
    tools = [
        connector_tool,  
        mcp_filesystem_tool, 
        mcp_geminicli_tool, 
        mcp_currency_conversion
    ],
    before_agent_callback=before_agent_callback,
    before_model_callback=before_model_callback,
    before_tool_callback=before_tool_callback,
    after_agent_callback=after_agent_callback,
    after_model_callback=after_model_callback,
    after_tool_callback=after_tool_callback,
)
