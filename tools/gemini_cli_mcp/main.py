import os
import sys
import subprocess
import shutil
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Gemini CLI Wrapper")

@mcp.tool()
def query_gemini(
    prompt: str,
    model: str = "gemini-2.5-flash-lite") -> str:
    """
    Invokes the local gemini-cli headlessly with a user prompt.
    
    Args:
        prompt: The text prompt to send to the Gemini model.
        model: The name of the Gemini model to use. Defaults to "gemini-2.5-flash".
        
    Returns:
        A string containing the combined Standard Output (stdout) 
        and Standard Error (stderr) from the CLI execution.
    """
    # VALIDATION: Check if the binary exists in the system PATH
    # Note: Replace 'gemini-cli' with the exact command name on your system 
    # (e.g., just 'gemini' or 'google-gemini' depending on how you installed it).
    cli_command = "gemini"
    
    if not shutil.which(cli_command):
        return (
            f"Error: The executable '{cli_command}' was not found in your PATH. "
            "Please ensure it is installed and available globally."
        )



    try:
        # EXECUTION: Run the process headlessly
        # We assume the CLI accepts the prompt as a command line argument.
        cmd = [
            cli_command,
            "--model", model,
            "--allowed-tools", "delegate_to_agent,run_terminal_command,run_shell_command",
            "--prompt", prompt,
            #"--include-directories", ".",
            "--yolo",
            #"--debug"
        ]

        #region secret - ADD API KEY
        my_env = os.environ.copy()
        my_env["GOOGLE_GENAI_USE_VERTEXAI"]="0"
        my_env["GEMINI_API_KEY"] = ""
        #endregion

        process = subprocess.run(
            cmd,
            capture_output=True, # Captures stdout and stderr
            text=True,           # Decodes output as string (not bytes)
            env=my_env,          # Pass environment variables
            cwd="/home/user/dev/google-ws-agent"
        )

        # 1. PRINT TO PARENT CONSOLE (DEBUGGING)
        # We manually write the captured output to the parent's stderr
        if process.stdout:
            sys.stderr.write(f"[Subprocess STDOUT]:\n{process.stdout}\n")
        if process.stderr:
            sys.stderr.write(f"[Subprocess STDERR]:\n{process.stderr}\n")
        sys.stderr.flush()

        # 2. RETURN TO MCP CLIENT (FUNCTION RESULT)
        # This is what the LLM/Claude actually sees
        full_output = process.stdout
        if process.stderr:
            full_output += f"\n[Errors]: {process.stderr}"
            
        return full_output

    except Exception as e:
        return f"System Error executing CLI: {str(e)}"

if __name__ == "__main__":
    # Runs the server using stdio communication
    mcp.run()