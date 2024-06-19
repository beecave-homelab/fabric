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

# Run the expect script to setup fabric
RUN /home/fabric-user/fabric_setup.exp

# Expose necessary ports and set command
EXPOSE 13337
EXPOSE 13338
CMD ["fabric-webui"]
# CMD ["fabric-api"]