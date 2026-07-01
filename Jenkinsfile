pipeline {
    agent any

    environment {
        DEPLOY_DIR = '/home/jin/placement-tracker'
    }

    stages {
        stage('Sync code') {
            steps {
                sh '''
                    rsync -a --delete \
                        --exclude ".git" \
                        --exclude "backend/venv" \
                        --exclude "backend/.env" \
                        --exclude "backend/uploads" \
                        --exclude "frontend/node_modules" \
                        --exclude "frontend/dist" \
                        --exclude "frontend/.env" \
                        ./ ${DEPLOY_DIR}/
                '''
            }
        }

        stage('Backend deps') {
            steps {
                sh '''
                    cd ${DEPLOY_DIR}/backend
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -q -r requirements.txt
                '''
            }
        }

        stage('Frontend build') {
            steps {
                sh '''
                    cd ${DEPLOY_DIR}/frontend
                    echo "VITE_API_BASE=/api" > .env
                    npm install --silent
                    npm run build
                '''
            }
        }

        stage('Restart services') {
            steps {
                sh '''
                    sudo systemctl restart placement-backend
                    sudo systemctl restart placement-frontend
                '''
            }
        }
    }

    post {
        success {
            echo 'Deployed successfully.'
        }
        failure {
            echo 'Build or deploy failed — services were not restarted.'
        }
    }
}
