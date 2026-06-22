pipeline {
    agent any

    environment {
        DOCKER_HUB_USER = 'numbush'
        BACKEND_IMAGE = "${DOCKER_HUB_USER}/sports-betting-backend"
        FRONTEND_IMAGE = "${DOCKER_HUB_USER}/sports-betting-frontend"
    }

    stages {

        stage('Checkout') {
            steps {
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

        stage('Deploy to Kubernetes') {
            steps {
                echo 'Deploying to Kubernetes...'
                sh "kubectl set image deployment/backend backend=${BACKEND_IMAGE}:${BUILD_NUMBER} -n sports-betting-dev"
                sh "kubectl set image deployment/frontend frontend=${FRONTEND_IMAGE}:${BUILD_NUMBER} -n sports-betting-dev"
                sh "kubectl rollout status deployment/backend -n sports-betting-dev"
                sh "kubectl rollout status deployment/frontend -n sports-betting-dev"
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