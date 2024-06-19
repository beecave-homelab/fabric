#####################
### Dockerfile v1 ###
#####################
# FROM ubuntu:22.04 AS fabric-base
# RUN apt update -y \
#     && apt install sudo -y \
#     && apt install python3 -y

# # Setup fabric user, workdir and copy files  
# COPY sudo-nopasswd /etc/sudoers.d/sudo-nopasswd
# RUN useradd --create-home -G sudo,video --shell /bin/bash fabric-user
# WORKDIR /home/fabric-user/
# USER fabric-user
# COPY . /home/fabric-user/fabric
# # ENV PATH="${PATH}:/home/fabric-user/fabric"

# RUN sudo apt update -y \
#     && sudo apt install python3 -y \
#     && sudo apt install pipx -y

# # Install fabric
# # RUN pipx install fabric
# RUN cd fabric \
#     && pipx install .
# # RUN pipx ensurepath
# ENV PATH="${PATH}:/home/fabric-user/.local/bin"

# FROM fabric-base AS fabric-setup

# WORKDIR /home/fabric-user/fabric
# USER fabric-user

# # Setup ollama
# # And if your server needs authentication tokens, as Blablador does, you export the token the same way you would with OpenAI:
# ENV OPENAI_BASE_URL=https://ollama.beecave-homelab.com/v1/
# ENV DEFAULT_MODEL="elvee/hermes-2-pro-llama3-instruct-merged-DPO:8b_q5_K_M"
# ENV OPENAI_API_KEY="sk-1234"
# # RUN fabric --setup
# # RUN pipx run fabric --setup
# # Enter settings for fabric (manually for now)
# # docker exec -it fabric /bin/bash
# # fabric --setup

# # Start fabric
# EXPOSE 13337
# EXPOSE 13338
# # CMD ["/bin/bash", "fabric-webui"]
# CMD ["/bin/sh"]

#####################
### Dockerfile v2 ###
#####################
FROM python:3.10 AS fabric-base

# Install sudo and expect
RUN apt-get update -y \
    && apt-get install -y sudo expect ffmpeg \
    && pip install --upgrade pip pipx \
    && apt-get clean

# Setup fabric user, workdir, and copy files
COPY sudo-nopasswd /etc/sudoers.d/sudo-nopasswd
RUN useradd --create-home -G sudo --shell /bin/bash fabric-user
WORKDIR /home/fabric-user/
USER fabric-user

# Copy project files and install dependencies
COPY . /home/fabric-user/fabric
RUN pipx install /home/fabric-user/fabric
ENV PATH="${PATH}:/home/fabric-user/.local/bin"

# Create an expect script to automate fabric --setup
RUN echo '#!/usr/bin/expect\n\
spawn fabric --setup\n\
expect "Please enter your OpenAI API key. If you do not have one or if you have already entered it, press enter."\n\
send "\r"\n\
expect "Please enter your claude API key. If you do not have one, or if you have already entered it, press enter."\n\
send "\r"\n\
expect "Please enter your Google API key. If you do not have one, or if you have already entered it, press enter."\n\
send "\r"\n\
expect "Please enter your YouTube API key. If you do not have one, or if you have already entered it, press enter."\n\
send "\r"\n\
interact' > /home/fabric-user/fabric_setup.exp \
    && chmod +x /home/fabric-user/fabric_setup.exp

FROM fabric-base AS fabric-setup

WORKDIR /home/fabric-user/fabric
USER fabric-user

# Setup ollama environment variables
ENV OPENAI_BASE_URL=https://ollama.beecave-homelab.com/v1/
ENV DEFAULT_MODEL="elvee/hermes-2-pro-llama3-instruct-merged-DPO:8b_q5_K_M"
ENV OPENAI_API_KEY="sk-1234"

# Run the expect script to setup fabric
RUN /home/fabric-user/fabric_setup.exp

# Expose necessary ports and set command
EXPOSE 13337
EXPOSE 13338
# ENTRYPOINT ["/bin/sh"]
CMD ["fabric-webui"]