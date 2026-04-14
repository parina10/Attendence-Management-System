pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "attendance-system"
        DOCKER_TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Clone Repository') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                // We use 'bat' for Windows and double backslashes for paths
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                // Running the test file using the python executable in the venv
                bat "venv\\Scripts\\python -m pytest test_app.py"
            }
        }

        stage('Build Docker Image') {
            steps {
                // In Windows Batch, we use %VAR% instead of ${VAR} inside double quotes
                bat "docker build -t %DOCKER_IMAGE%:%DOCKER_TAG% ."
                bat "docker tag %DOCKER_IMAGE%:%DOCKER_TAG% %DOCKER_IMAGE%:latest"
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        failure {
            echo 'Pipeline failed! Check the console output for errors.'
        }
    }
}
