## Setup
```sh
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

pip install google-adk[a2a]
```

## Start the remote A2A agent server using uvicorn

```sh
A2A_HOST="localhost"
A2A_PORT=8877
ENV_VAR_FILEPATH="./google_drive_agent/.env"

# Run the remote A2A agent (server)
uvicorn google_drive_agent.a2a_agent:a2a_app --host $A2A_HOST --port $A2A_PORT --env-file $ENV_VAR_FILEPATH

# check remote agent is running
curl http://$A2A_HOST:$A2A_PORT/.well-known/agent-card.json
```

## Establish ngrok API tunnel

1. Install [ngrok](https://ngrok.com/download/linux)
1. Start endpoint
    ```sh
    # load auth key
    source ./google_drive_agent/.ngrok

    # create tunnel and get public url
    ngrok http $A2A_PORT --host-header=$A2A_HOST:$A2A_PORT
    PUBLIC_URL_TUNNEL=$(ngrok api tunnels list --api-key $NGROK_APIKEY | jq --raw-output '.tunnels[0].public_url')
    ```
  
1. Check remote agent
    ```sh
    A2A_AGENT_CARD=$(curl $PUBLIC_URL_TUNNEL/.well-known/agent-card.json)
    echo $A2A_AGENT_CARD
    ```

## Register Gemini Enterprise A2A agent

1. In your Gemini Enterprise instance add a new A2A agent. Use the agent card json of your locally running agent
    > Attention: Replace the localhost host URI with the public (ngrok) one (which was retrieve in the previous step) 
