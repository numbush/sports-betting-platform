# Custom Jenkins image: LTS base + Docker CLI + kubectl + Helm for full in-cluster CI/CD
FROM jenkins/jenkins:lts

USER root

RUN apt-get update && \
    apt-get install -y docker.io curl git python3 python3-pip && \
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash && \
    usermod -aG docker jenkins && \
    rm -rf /var/lib/apt/lists/*

# Pre-configure git safe.directory — avoids "dubious ownership" when Jenkins clones repos as root-owned volumes
# Create gitconfig for jenkins user
RUN mkdir -p /var/jenkins_home && \
    echo '[safe]\n\tdirectory = *' > /var/jenkins_home/.gitconfig && \
    chown -R jenkins:jenkins /var/jenkins_home/.gitconfig

USER jenkins