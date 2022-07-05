- [Vendor Updates Content](#vendor-updates-content)
  - [CMS](#cms)
    - [Djangoapps](#djangoapps)
    - [Envs](#envs)
    - [Static](#static)
    - [Templates](#templates)
    - [CMS Core Files](#cms-core-files)
  - [Common](#common)
    - [Djangoapps](#djangoapps-1)
    - [Lib](#lib)
    - [Static](#static-1)
    - [Templates](#templates-1)
  - [Conf/locale](#conflocale)
  - [LMS](#lms)
    - [Djangoapps](#djangoapps-2)
    - [Envs](#envs-1)
    - [Static](#static-2)
    - [Templates](#templates-2)
    - [Core](#core)
  - [Openedx/core](#openedxcore)
  - [Openedx](#openedx)
- [Vendor Update Path](#vendor-update-path)
  - [Install Requirements while testing when a container asks for it.](#install-requirements-while-testing-when-a-container-asks-for-it)
    - [pip](#pip)
  - [Install statics](#install-statics)
  - [Install templates](#install-templates)
    - [Dependencies](#dependencies)
    - [Dependencies](#dependencies-1)
  - [Install CMS Additions](#install-cms-additions)
    - [Facets](#facets)
  - [Install Common Djangoapps](#install-common-djangoapps)
  - [Install Common Lib](#install-common-lib)
  - [Check the status](#check-the-status)
  - [Install LMS Djangoapps](#install-lms-djangoapps)
  - [Install Open edX Additions](#install-open-edx-additions)
  - [LMS](#lms-1)
  - [Configure LMS Envs](#configure-lms-envs)
- [TODO](#todo)
  - [Test current set up](#test-current-set-up)
  - [Check additional config files and compare to current ones](#check-additional-config-files-and-compare-to-current-ones)
  - [Check pip in minicourse to see if anything is missing](#check-pip-in-minicourse-to-see-if-anything-is-missing)
- [False Alarm](#false-alarm)
- [CSRF Location](#csrf-location)
  - [Error occurred after Student Views is added](#error-occurred-after-student-views-is-added)
    - [Start from the templates](#start-from-the-templates)
    - [Start again from the LMS templates](#start-again-from-the-lms-templates)

# Vendor Updates Content

## CMS

### Djangoapps
* Contentstore
* Models -> Add contentstore

### Envs
* Add together with tutor

### Static
Add as it is.

### Templates
Add as it is.

### CMS Core Files
* celery
* urls
  
## Common

### Djangoapps
* Facet `(vendor addition)`
  * Add everything in this directory.
* PDF_XBlock `(vendor addition)`
  * Add everything in this directory.
* Recommendations `(vendor addition)`
  * Add everything in this directory.
* Student
  * Possible CSRF culprit.
  * Do not add yet.
* Third party auth
  * Check carefully.

### Lib
* XModule
  * Add directly.

### Static
* Add directly.
  
### Templates
* Add directly.

## Conf/locale
* Add the config.yaml

## LMS

### Djangoapps
* Branding
* Courseware
* Homepage_setting
* Instructor_task
* Mobile_api

### Envs
* Add common, production to tutor

### Static
Add everything.

### Templates
Add everything.

### Core
* celery
* urls

## Openedx/core
* A lot of changes.

## Openedx
* views
* features → static 
  
# Vendor Update Path

## Install Requirements while testing when a container asks for it.
### pip
```
pip install aliyun-python-sdk-core
```

## Install statics
* CMS
* LMS
* Common

## Install templates
* CMS
### Dependencies
* Recommendation
  * Common/Djangoapps/Recommendation
  * CMS/Djangoapps/Contentstore/views/course.py
    * Also dependency for facet 
  * CMS/envs/common.py
    * Also dependency for facet
  * Run Migrations from inside the cms container
  ```
  ./manage.py cms migrate
  ```
  * 
* Facet
  * Mentioned in index.html, cms/envs/common.py, course.py
  * Commmon/Djangoapps/Facet
  * Contentstore/views/ facet_group.py, __init__.py
  * Contentstore/utils
  * Run migrations -> no need to run the ones above unless MySQL is closed.

* Common
  * Single file

* LMS templates
### Dependencies
* Homepage Settings
  * LMS/Djangoapps/Homepage Settings
    * LMS/envs/common.py -> require settings
  * Run migrations
  ```
  ./manage.py lms migrate
  ```
  * Depends on Student Views
  * Common/Djangoapps/Student/Views/management.py
    * Depends on CourseOverview
    * openedx\core\djangoapps\content\course_overviews
    * Needs a specific model from this directory -> migrations
    * Run migrations
  * Disable the login view additions to check 
  * Check CMS status
  
## Install CMS Additions
### Facets
* CMS/Djangoapps/Contentstore/utils.py
* CMS/Djangoapps/Models/settings/course_metadata.py
* CMS/urls.py

Check if facets work.
* Enable courseoverviewexpansion in the fields.
* Enable check_user_is_teacher when added.
* Enable user_displayname when added.
* They don't due to error with JS.

* Add pdf_xblock
  * Common/Djangoapps/Pdf_Xblock
  
## Install Common Djangoapps
* Run LMS
* Add student, third_party_auth

## Install Common Lib
* lib xmodule/course_module
  
## Check the status
* *Roll back* to latest version
  Latest version: \openedx\core\djangoapps\content\course_overviews\migrations\0026_auto_20210930_1214.py
  ```
  ./manage.py lms makemigrations course_overviews
  ./manage.py lms migrate course_overviews 0025
  ./manage.py lms migrate course_overviews 0026
  ```
  CSRF again -> check why -> false alarm

## Install LMS Djangoapps
* Branding
* Courseware/Views/Views.py
* Instructor_tasks/tests/test_tasks_helper.py -> Whitespace
* Mobile_api/users/serializer.py
* Enable user_displayname

## Install Open edX Additions
* Core/Djangoapps
  * Models
  * Oauth_dispatch
  * User_api
  * User_authn
* Features/learner_profile

## LMS
* Urls
  * Add facet and pdf_xblock support

## Configure LMS Envs


# TODO
## Test current set up
## Check additional config files and compare to current ones
* lms.yaml
* cms.yaml
## Check pip in minicourse to see if anything is missing  

# False Alarm  
Error occurs due to networking, not related to modification.
# CSRF Location
## Error occurred after Student Views is added
### Start from the templates

* Remove the student_account template to return the login page to previous version
* Still CSRF
* Not a template issue
* Remove static js student_account
* Remove all the changes 
  * student/views/management.py
  * lms djangoapps homepage_setting
  * lms env common
  * lms templates
  * open edx core djangoapps content courseoverview
* Possibly the migrations causing the error
  * Stop all services
  * Delete all the dev containers
  * Start normally
  * This CSRF was caused by the domain mismatch -> change config
  ```
  tutor config save --interactive
  ```
  * `local.overhang.io` is whitelisted in this config

### Start again from the LMS templates
* Follow the path above.
* Now working.
* Check with alienware domain.
  * The domain causes CSRF error.

