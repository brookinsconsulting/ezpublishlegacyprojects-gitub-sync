# ezpublishlegacyprojects-github-sync

A simple custom and private solution building and importing project.ez.no subversion repositories and downloads into github repositories.

Note: This solution is alpha quality at best.

# Usage

## Direct python execution, Required Parameters Only (Within interactive shell only)

     ~/bin/ezpublishlegacyprojects-github-sync/bin/import_project_resources.py --token=<github-personal-access-token-string> --delete_empty_repos=True --github_hostname='github-as-ezpublishlegacyprojects' --account='ezpublishlegacyprojects' --base_path='/home/brookins/ezecosystem/projects.mirror.ezecosystem.org/';

## Direct execution, Remove all empty projects

    ~/bin/ezpublishlegacyprojects-gitub-sync/bin/import_project_resources.py --token=<github-personal-access-token-string> --delete_empty_repos=True --github_hostname='github-as-ezpublishlegacyprojects' --account='ezpublishlegacyprojects' --base_path='/home/brookins/ezecosystem/projects.mirror.ezecosystem.org/' --subversion_only=False --subversion_import=False --download_only=False --download_import=False --verbose=True

# Required projects.ez.no httrack mirror

- Requires complete static html httrack mirror of all projects.ez.no resources


# Required specific directory strucuture
- /tmp/projects.ez.no/doc
- /tmp/projects.ez.no/mirror
- /tmp/projects.ez.no/mirror/subversion
- /tmp/projects.ez.no/mirror/downloads
- /tmp/projects.ez.no/mirror/repositories


# Required software

- GNU/Linux
- bash, 4.1.2(1)-release
- python, 2.6.6 (or version =< 2.6.9)
- pip, ?rev
- github pip module, ?rev
- gitpython pip module, ?rev
- unittest2 pip module, ?rev
- argparse pip module, ?rev
- git, 2.1.2
- find, ?rev
- rsync, ?rev
- coreutils, ?rev
- 


## Github Access Requires

- eZPublishLegacy github.com user access
- eZPublishlegacyProjectsRobot Application Personal Access Token
- eZPublishlegacyProjectsRobot Application Client ID and Secret

