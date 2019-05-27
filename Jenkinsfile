pipeline {
  agent any

  environment {
    REPO_NAME = 'bpt-torch'
    PACKAGE = "bpttorch"

    GITHUB_USER = 'bardel-jenkins'
    GITHUB_TOKEN = credentials('github-api-token')
    SONAR_TOKEN = credentials('sonarcloud-token')
    PYPI_TOKEN = credentials('jenkins-pypi')

    SENTRY_URL = "https://sentry.bardel.ca"
    SENTRY_ORG = "bardel"
    SENTRY_AUTH_TOKEN = credentials('sentry-auth-token')
  }

  stages {

    stage("Build and Deploy") {
      parallel {

        stage('Linux') {
          stages {

            stage('Check Merge') {
              steps {
                sh '''
                eval "$(dev --no-color --dry-run env python)"
                dev check-version
                dev build -a
                dev test
                '''
              }
            }// stage("Check Merge")

            stage("Publish Python wheel") {
              when { branch 'master' }
              steps {
                sh '''
                pip install twine
                twine upload \
                  --repository-url http://pypi.apps.corp.bardel.ca build/*.whl \
                  --username "$PYPI_TOKEN_USR" \
                  --password "$PYPI_TOKEN_PSW" \
                  --verbose \
                  --skip-existing
                '''
              }
            }// stage("publish Python Wheel")

          }// stages
        }// stage('Linux')

      }// parallel
    }// stage("Build and Deploy")

    stage('Release') {
      when { branch 'master' }
      steps {
        sh '''
        github-release release \
          --user bardel-tech \
          --security-token "$GITHUB_TOKEN" \
          --repo $REPO_NAME \
          --tag v$(dev query {{.Version}}) \
          --name "v$(dev query {{.Version}})" \
          --description "Release $(dev query {{.Version}})"
        '''
        sh '''
        VERSION="${PACKAGE}@$(dev query {{.Version}})"
        sentry-cli releases new -p $REPO_NAME $VERSION
        sentry-cli releases set-commits --auto $VERSION
        '''
      }
    } // stage('Release')

  }// stages

  post {
    failure {
      script {
        if (env.BRANCH_NAME == 'master') {
          slackSend channel: "#core-dev",
                color: 'danger',
                message: "deployment failed ${env.JOB_NAME} ${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)"
        }
      }
    }
  }

}
