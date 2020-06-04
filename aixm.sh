#!/usr/bin/env bash
set -e

LOGFILE="./log/aixm.log"

check_log() {
  echo "Check $LOGFILE for more details."
}

docker_build() {
  docker build -t aixm-graph:latest .
}

docker_start() {
  docker run -d --name aixm_graph \
    -e "PORT=8765" \
    -p 3000:8765 \
    -v "$PWD"/config/features.json:/app/aixm_graph/features_config.json \
    -v "$PWD"/config/icons:/usr/share/nginx/html/feature_icons \
    aixm-graph:latest
}

docker_stop() {
  docker rm -f aixm_graph
}

git_pull() {
  git pull --rebase origin master
}

install() {
  echo "This might take a few minutes. You can check the progress with 'tail -f ./log/aixm.log' in a separate shell"
  cp ./misc/features.json ./config/features.json
  mkdir log 2> /dev/null
  docker_build > $LOGFILE 2>&1 &&
  echo -e "\nInstallation completed successfully!" ||
  (echo -e "\nInstallation failed!" && check_log)
}

start() {
  docker_start > /dev/null 2> $LOGFILE &&
  echo "Started and running on http://0.0.0.0:3000/" ||
  ([[ $(grep -c "Conflict" $LOGFILE) -eq 1 ]] &&
   echo "AIXM Graph is already started." ||
   echo "Failed to start AIXM Graph." &&
   check_log)
}

stop() {
  docker_stop > /dev/null 2> $LOGFILE &&
  echo "Stopped AIXM Graph" ||
  ([[ $(grep -c "No such container" $LOGFILE) -eq 1 ]] &&
   echo "AIXM Graph is not started." ||
   echo "Failed to stop AIXM Graph." &&
   check_log)
}

update() {
  CURRENT_VERSION=$(version)

  git_pull > $LOGFILE 2>&1 || (echo "Update failed!" && check_log && exit 1)

  if [[ $CURRENT_VERSION = $(version) ]]
  then
    echo "There is not any available update."
  else

    docker_stop > /dev/null 2> $LOGFILE ||
    echo "This might take a few minutes. You can check the progress with 'tail -f ./log/aixm.log' in a separate shell" &&
    docker_build > $LOGFILE 2>&1 &&
    echo "AIXM Graph was updated successfully to version $(version)" ||
    (echo "Update failed!" && check_log)
  fi
}

usage() {
  echo -e "Usage: aixm.sh [COMMAND]\n"
  echo "Commands:"
  echo "    install    Builds the docker image and prepares the features' configuration"
  echo "    start      Instantiates the docker image by creating a docker container"
  echo "    stop       Stops the running container"
  echo "    update     Pulls the newest version and re-installs the app"
  echo "    version    Prints the version of the app"
  echo "    help       Prints the available options"
  echo ""
}

version() {
  grep VUE_APP_VERSION < ./client/.env | colrm 1 16
}

ACTION=${1}

case ${ACTION} in
  install)
    install
    ;;
  start)
    start
    ;;
  stop)
    stop
    ;;
  update)
    update
    ;;
  help)
    usage
    ;;
  version)
    version
    ;;
  *)
    echo -e "Invalid action\n"
    usage
    ;;
esac
