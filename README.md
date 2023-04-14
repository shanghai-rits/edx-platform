# Quickstart Development with Tutor

## Versions

Tutor: 12.2.0

-  https://github.com/overhangio/tutor/releases/tag/v12.2.0
-  https://pypi.org/project/tutor/12.2.0/

Python: 3.8.12

Open edX: open-release/lilac.3

- https://github.com/edx/edx-platform/tree/open-release/lilac.3


## Create Python Environment

```bash
pyenv virtualenv 3.8.12 tutor-lilac
pyenv local tutor-lilac
```

## Install Tutor 12.2.0 Inside the Virtual Environment

```bash
pip install tutor==12.2.0
```

## Add the Environment Variable to Change the Default Tutor Environment

You can use `direnv` to do the auto environment variable addition.

```bash
export TUTOR_ROOT=PROJECT_DIR/tutor
export TUTOR_PLUGINS_ROOT=PROJECT_DIR/tutor-plugins
```

## Set up the Tutor Config

Add the following variables to the config file `PROJECT_DIR/tutor/config.yml`

```bash
CMS_HOST: studio.local.overhang.io
CONTACT_EMAIL: email@example.com
DOCKER_IMAGE_OPENEDX: docker.io/<REPO>/openedx:12.2.0
ENABLE_HTTPS: false
LANGUAGE_CODE: en
LMS_HOST: local.overhang.io
OPENEDX_EXTRA_PIP_REQUIREMENTS:
- aliyun-python-sdk-core
PLATFORM_NAME: Test MOOC Lilac
PLUGINS:
- notes
- thirdparty-wechat
```

Change the name of the containers to avoid conflict using the variable `LOCAL_PROJECT_NAME`
Write the variables inside the `PROJECT_DIR/tutor/config.yml` file

```bash
LOCAL_PROJECT_NAME: tutor_lilac
DEV_PROJECT_NAME: tutor_lilac_dev
```

## Set up the Plugins
Create the plugins root at `PROJECT_DIR/tutor-plugins` and add the **thirdparty-wechat** plugin.

PROJECTDIR/tutor-plugins/myplugin.yml
```YAML
name: thirdparty-wechat
version: 0.1.0
patches:
  common-env-features: |
    "ENABLE_THIRD_PARTY_AUTH": false
  openedx-auth: |
    "SOCIAL_AUTH_OAUTH_SECRETS": {
      "weixin": ""
    }
```

## Start Tutor

```bash
tutor config save
tutor local quickstart
```

## Create the Dev image

```bash
tutor images build openedx-dev
tutor local stop
tutor dev start
```

## Push the Dev Image to Docker Hub - optional

Add the following variable to `PROJECT_DIR/tutor/config.yml`

```bash
DOCKER_IMAGE_OPENEDX_DEV: docker.io/<REPO>/openedx-dev:12.2.0
```

```bash
tutor dev stop
tutor config save
tutor images build openedx-dev
```

Push the Image from Docker Desktop GUI.

## Set up the Dev Environment

Unshallow optional.

```bash
tutor dev bindmount lms /openedx/edx-platform
git fetch --unshallow origin
```

Add the following dev docker compose override at the location `tutor/env/dev/docker-compose.override.yml`
**MySQL port expose is optional.**

```YAML
version: "3.7"
services:
  mysql:
    ports:
      - "3306:3306"
  lms:
    volumes:
      - "PROJECT_DIR/tutor/volumes/edx-platform:/openedx/edx-platform"
  cms:
    volumes:
      - "PROJECT_DIR/tutor/volumes/edx-platform:/openedx/edx-platform"
  lms-worker:
    volumes:
      - "PROJECT_DIR/tutor/volumes/edx-platform:/openedx/edx-platform"
  cms-worker:
    volumes:
      - "PROJECT_DIR/tutor/volumes/edx-platform:/openedx/edx-platform"
```

The code can now be edit from the PROJECT_DIR/tutor/volumes/edx-platform location.

Start developing by running the start command.
```bash
tutor dev start
```
