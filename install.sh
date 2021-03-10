#!/usr/bin/env bash

usage="VPMBench installer, version 0.1
where:
    -h  show this help text

All further settings will be specified in a yes/no dialog.
    "

while getopts ':h' option; do
  case "$option" in
  h)
    echo "$usage"
    exit
    ;;
  \?)
    printf "illegal option: -%s\n" "$OPTARG" >&2
    echo "$usage" >&2
    exit 1
    ;;
  esac
done
shift $((OPTIND - 1))

set -e

SCRIPT=$(readlink -f "$0")
BASEDIR=$(dirname "$SCRIPT")

cd $BASEDIR

echo "#####################################"
echo "Guided Installation for VPMBench-v0.1"
echo "#####################################"
echo ""

echo "The following questions will guide you through selecting the files and dependencies needed for VPMBench."
echo "After this, you will see an overview before the download and installation starts."
echo ""

#Plugin path
read -p "Where do you want to store the plugins? [~/VPMBench-Plugins] " PLUGIN_PATH

PLUGIN_PATH=$(eval echo $PLUGIN_PATH)
if [ -z $PLUGIN_PATH ]; then
  PLUGIN_PATH=~/VPMBench-Plugins
fi

if [ -e $PLUGIN_PATH ]; then
  echo "ERROR: Directory $PLUGIN_PATH already exists"
  exit 1
fi

#Docker setup
read -p "Do you want to test if Docker works? (y)/n" CHOICE
case "$CHOICE" in
y | Y) TEST_DOCKER=true ;;
n | N) TEST_DOCKER=false ;;
*)
  TEST_DOCKER=true
  echo "> Assuming YES."
  ;;
esac
echo ""

#Copy Plugins
read -p "Do you want to copy the provided plugin to $PLUGIN_PATH? (y)/n " CHOICE
case "$CHOICE" in
y | Y) COPY_PLUGINS=true ;;
n | N) COPY_PLUGINS=false ;;
*)
  COPY_PLUGINS=true
  echo "> Assuming YES."
  ;;
esac
echo ""

# Install plugins
if [ "$COPY_PLUGINS" = true ]; then
  read -p "Do you want to install the provided plugins (Warning: Might take a while)? (y)/n " CHOICE
  case "$CHOICE" in
  y | Y) INSTALL_PLUGINS=true ;;
  n | N) INSTALL_PLUGINS=false ;;
  *)
    INSTALL_PLUGINS=true
    echo "> Assuming YES."
    ;;
  esac
  echo ""
fi

if [ "$INSTALL_PLUGINS" = true ]; then
  read -p "Do you want to install CADD (~ 200GB, Warning: Sometimes the installation seems to fail for no obvious reasons)? (y)/n" CHOICE
  case "$CHOICE" in
  y | Y) INSTALL_CADD=true ;;
  n | N) INSTALL_CADD=false ;;
  *)
    INSTALL_CADD=true
    echo "> Assuming YES."
    ;;
  esac
  echo ""

  read -p "Do you want to fathmm-MKL (~80GB)? (y)/n" CHOICE
  case "$CHOICE" in
  y | Y) INSTALL_FATHMM_MKL=true ;;
  n | N) INSTALL_FATHMM_MKL=false ;;
  *)
    INSTALL_FATHMM_MKL=true
    echo "> Assuming YES."
    ;;
  esac
  echo ""

  if [ "$INSTALL_FATHMM_MKL" = true ]; then
    if ! type "tabix" >/dev/null; then
      echo '> ERROR: Tabix seems not to be installed in the current $PATH. Please install tabix to install fathmm-MKL'
      exit 1
    fi
  fi

  read -p "Do you want to do a test run after the installation? (y)/n"
  case "$CHOICE" in
  y | Y) TEST_RUN=true ;;
  n | N) TEST_RUN=false ;;
  *)
    TEST_RUN=true
    echo "> Assuming YES."
    ;;
  esac
  echo ""
fi

echo ""

# Summary
echo "Summary"
echo "========"
echo "* Plugin Path: $PLUGIN_PATH"
echo "* Test Docker: $TEST_DOCKER"
echo "* Copy provided plugins: $COPY_PLUGINS"
if [ "$COPY_PLUGINS" = true ]; then
  echo "* Install provided plugins: $INSTALL_PLUGINS"
  if [ "$INSTALL_PLUGINS" = true ]; then
    echo "  - Install CADD: $INSTALL_CADD"
    echo "  - Install fathmm-MKL: $INSTALL_FATHMM_MKL"
    echo "  - Test run: $INSTALL_FATHMM_MKL"
    echo "Please make sure you have enough disk space available to install the plugins."
  fi
fi
echo "Please make sure you have the rights to run docker and install python packages!"
echo ""
echo ""
read -p "Ready to continue? (y)/n " CHOICE
case "$CHOICE" in
n | N)
  echo "You canceled the installation."
  exit 0
  ;;
*) echo "Starting installation. This will take some time." ;;
esac
echo ""
echo ""
echo ""
echo "################"
echo "Install VPMBench"
echo "################"
echo ""
echo ""
############### INSTALLATION
echo "> Test Docker"
docker run hello-world >/dev/null

if [ $? -ne 0 ]; then
  echo "Can't run Docker. Install Docker and check permissions!"
  exit 1
fi

echo "> Create $PLUGIN_PATH"
mkdir -p $PLUGIN_PATH

if [ "$COPY_PLUGINS" = true ]; then
  if [ "$INSTALL_PLUGINS" = true ]; then
    echo "> Install Plugins"
    if [ "$INSTALL_CADD" = true ]; then
      echo ""
      echo ""
      cp -r $BASEDIR/plugins/cadd $PLUGIN_PATH/
      sh $PLUGIN_PATH/cadd/install.sh
    fi
    if [ "$INSTALL_FATHMM_MKL" = true ]; then
      echo ""
      echo ""
      cp -r $BASEDIR/plugins/fathmm $PLUGIN_PATH/
      sh $PLUGIN_PATH/fathmm/install.sh
    fi
  fi
  echo ""
  echo "THE INSTALLATION OF THE PLUGINS IS DONE"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
fi

echo "> Install python package"
pip install --user --ignore-installed .

if [ "$TEST_RUN" = true ]; then
  python $BASEDIR/bin/after_install.py $BASEDIR/tests/resources/test_grch37.vcf $PLUGIN_PATH
fi
