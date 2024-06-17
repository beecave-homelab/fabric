FROM ubuntu:22.04

# Install requirements. Setup pipx
RUN apt update -y \
    && apt install python3 -y \
    && apt install pipx -y \
    && pipx ensurepath
    # optional to allow pipx actions with --global argument
    # && pipx ensurepath --global

# Setup workdir and copy files    
COPY . /fabric

# Install fabric
# RUN pipx install fabric
WORKDIR /fabric
RUN pipx install .

# Setup ollama
# And if your server needs authentication tokens, as Blablador does, you export the token the same way you would with OpenAI:
ARG OPENAI_BASE_URL=https://ollama.beecave-homelab.com/v1/
ARG DEFAULT_MODEL="elvee/hermes-2-pro-llama3-instruct-merged-DPO:8b_q5_K_M"
ARG OPENAI_API_KEY="sk-1234"
RUN cd /fabric
RUN fabric --setup
# Enter settings for fabric (manually for now)
# docker exec -it fabric /bin/bash
# fabric --setup

# Start fabric
# EXPOSE 13337
# EXPOSE 13338
# RUN fabric-webui
