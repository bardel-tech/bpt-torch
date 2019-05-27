pipeline {
    agent any

    stages {
        stage("pytest") {
            sh '''
            eval "$(dev --no-color --dry-run env python)"
            pytest
            '''
        }
    }
}
