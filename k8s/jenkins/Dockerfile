FROM jenkins/jenkins:lts

USER root

RUN apt-get update && \
    apt-get install -y docker.io curl git && \
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    usermod -aG docker jenkins && \
    rm -rf /var/lib/apt/lists/*

# Create gitconfig for jenkins user
RUN mkdir -p /var/jenkins_home && \
    echo '[safe]\n\tdirectory = *' > /var/jenkins_home/.gitconfig && \
    chown -R jenkins:jenkins /var/jenkins_home/.gitconfig

USER jenkins