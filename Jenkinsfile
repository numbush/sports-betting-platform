pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'giladkr'
        BACKEND_IMAGE = "${DOCKER_HUB_USER}/sports-betting-backend"
        FRONTEND_IMAGE = "${DOCKER_HUB_USER}/sports-betting-frontend"
    }

    stages {

        stage('Checkout') {
            steps {
                sh 'git config --global --add safe.directory "*"'
                echo 'Pulling code from Git...'
                checkout scm
            }
        }

        stage('Build Backend Image') {
            steps {
                echo 'Building backend Docker image...'
                sh "docker build -t ${BACKEND_IMAGE}:${BUILD_NUMBER} ./backend"
                sh "docker tag ${BACKEND_IMAGE}:${BUILD_NUMBER} ${BACKEND_IMAGE}:latest"
            }
        }

        stage('Build Frontend Image') {
            steps {
                echo 'Building frontend Docker image...'
                sh "docker build -t ${FRONTEND_IMAGE}:${BUILD_NUMBER} ./frontend"
                sh "docker tag ${FRONTEND_IMAGE}:${BUILD_NUMBER} ${FRONTEND_IMAGE}:latest"
            }
        }

        stage('Push to Docker Hub') {
            steps {
                echo 'Pushing images to Docker Hub...'
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh "echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin"
                    sh "docker push ${BACKEND_IMAGE}:${BUILD_NUMBER}"
                    sh "docker push ${BACKEND_IMAGE}:latest"
                    sh "docker push ${FRONTEND_IMAGE}:${BUILD_NUMBER}"
                    sh "docker push ${FRONTEND_IMAGE}:latest"
                }
            }
        }

        stage('Deploy to Dev') {
            steps {
                echo 'Deploying to Dev environment...'
                sh """
                    helm upgrade --install sports-betting ./helm/sports-betting-platform \
                    --namespace sports-betting-dev \
                    --create-namespace \
                    --set backend.image.tag=${BUILD_NUMBER} \
                    --set frontend.image.tag=${BUILD_NUMBER}
                """
                sh "kubectl rollout status deployment/backend -n sports-betting-dev"
                sh "kubectl rollout status deployment/frontend -n sports-betting-dev"
            }

        }

        stage('Deploy to Staging') {
            steps {
                echo 'Deploying to Staging environment...'
                sh """
                    helm upgrade --install sports-betting-staging ./helm/sports-betting-platform \
                    -f ./helm/sports-betting-platform/values-staging.yaml \
                    --namespace sports-betting-staging \
                    --create-namespace \
                    --set backend.image.tag=${BUILD_NUMBER} \
                    --set frontend.image.tag=${BUILD_NUMBER}
                """
                sh "kubectl rollout status deployment/backend -n sports-betting-staging"
                sh "kubectl rollout status deployment/frontend -n sports-betting-staging"
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed!'
        }
    }
}