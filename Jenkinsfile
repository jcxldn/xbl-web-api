// Scripted Pipeline
// Requires libraries from https://github.com/Prouser123/jenkins-tools
// Made by @Prouser123 for https://ci.jcx.ovh.

node('docker-cli') {
  postJobGhStatus() {
    scmCloneStage()
  
    useDockerImage('python:3-slim-buster') {

      stage('Install') {
        unstash 'scm'
		
		// codecov needs the git plugin to properly resolve the report.
	    sh 'apt-get update && apt-get install git -y  && pip install coverage codecov -r requirements.txt'
      }
	
	  stage('Test') {
	    withCredentials([usernamePassword(credentialsId: 'job-specific.xbl-web-api', passwordVariable: 'XBL_PASS', usernameVariable: 'XBL_EMAIL')]) {
	      sh 'coverage run tests.py'
        }
	  }
	
	  stage('Coverage') {
	    withCredentials([string(credentialsId: 'codecov.prouser123.xbl-web-api', variable: 'CODECOV_TOKEN')]) {
	      sh 'codecov'
	    }
	  }
    }
  
    // If on the master branch, deploy with GitHub status checks enabled.
    deployStage(true)
  }
}