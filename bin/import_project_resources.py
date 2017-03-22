#!/usr/bin/python

#
# Imports
#

import argparse
import os
import subprocess
import requests
import urllib3
import json
import github
import git

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import SNIMissingWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning
from github import Github, GithubException
from github.GithubObject import NotSet
from git import Repo

#
# Program Arguments
#

parser = argparse.ArgumentParser( # name='import_project_resources.py', # allow_abbrev=True,
                                  description='Import projects.ez.no project resources (subversion repositories and downloads) into git repositories into github.com/ezpublishlegacyprojects.' )
parser.add_argument('--token', type=str,
                    required=True,
                    help='the oauth or personal access token from git repository provider (Required. Default: none)')
parser.add_argument('--base_path', type=str,
                    required=False,
                    default='/home/brookins/ezecosystem/projects.mirror.ezecosystem.org/',
                    help='the full base path (Optional. Default: /home/brookins/ezecosystem/projects.mirror.ezecosystem.org/)')
parser.add_argument('--account', type=str,
                    required=False,
                    help='the name of the account from git repository provider (Optional. Default: ezpublishlegacyprojects)')
parser.add_argument('--local', type=str,
                    required=False,
                    default=True,
                    help='perform only local actions. Prevents pushing created repositories to git repository provider (Optional. Default: True)')
parser.add_argument('--limit', type=str,
                    required=False,
                    default=7500,
                    help='limit the number of projects this script actions process. Limits script actions (Optional. Default: 7500)')
parser.add_argument('--log_only', type=str,
                    required=False,
                    default=False,
                    help='logs subversion authors only. Prevents almost all other program action (Deprecated. Optional. Default: False)')
parser.add_argument('--subversion_only', type=str,
                    required=False,
                    default=False,
                    help='imports only subversion resources. Prevents creating subversion repositories (Optional. Default: False)')
parser.add_argument('--subversion_import', type=str,
                    required=False,
                    default=False,
                    help='import subversion resources. Creates git repositories and imports subversion repository files (Takes Exessively Long. Optional. Default: False)')
parser.add_argument('--download_only', type=str,
                    required=False,
                    default=False,
                    help='imports only download resources. Prevents creating download repositories (Optional. Default: False)')
parser.add_argument('--download_import', type=str,
                    required=False,
                    default=False,
                    help='import download resources. Creates git repositories and imports download repository files (Takes Exessively Long. Optional. Default: False)')
parser.add_argument('--delete_only', type=str,
                    required=False,
                    default=False,
                    help='delete all remote repositories. Removes git repositories from git repository provider. (Optional. Default: False)')
parser.add_argument('--order', type=str,
                    required=False,
                    default=False,
                    help='order of processing. Accepts: reverse (Optional. Default: False)')
parser.add_argument('--delete_empty_repos', type=str,
                    required=False,
                    default=False,
                    help='delete empty remote repositories. Removes git repositories from git repository provider. Deprecates --delete_only (Optional. Default: False)')
parser.add_argument('--debug_exit_print', type=str,
                    required=False,
                    default=False,
                    help='type of project to print list and exit. Accepts: subversion, downloads, or directories (Optional. Default: False)')
parser.add_argument('--verbose', type=str,
                    required=False,
                    default=False,
                    help='display verbose debug output (Optional. Default: False)')
parser.add_argument('--debug_level', type=int,
                    required=False,
                    default=0,
                    help='level of verbose debug output (Optional. Default: 0)')
parser.add_argument('--github_hostname', type=str,
                    required=False,
                    default='github.com',
                    help='the ssh github hostname. Useful for ssh identity aliases (Optional. Default: github.com)')

args = parser.parse_args()

# Arguments into variables
account = args.account
token = args.token
repository_hostname = args.github_hostname
base_path = args.base_path
limit = args.limit
order = args.order
verbose = args.verbose
debug_level = args.debug_level

local = args.local
log_only = args.log_only
subversion_only = args.subversion_only
subversion_import = args.subversion_import
download_import = args.download_import
download_only = args.download_only
delete_only = args.delete_only
delete_empty_repos = args.delete_empty_repos

# Process debug_exit_print arguments
if args.debug_exit_print != False:
    debug_exit_print_subversion = False
    debug_exit_print_downloads = False
    debug_exit_print_directories = False
    if args.debug_exit_print == 'subversion':
        debug_exit_print_subversion = True
    elif args.debug_exit_print == 'downloads':
        debug_exit_print_downloads = True
    elif args.debug_exit_print == 'directories':
        debug_exit_print_directories = True
else:
    debug_exit_print_subversion = False
    debug_exit_print_downloads = False
    debug_exit_print_directories = False

# Disable SSL Related Warnings (We already know we have old tools)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Calculated Path Items
path = base_path + 'doc/'
mirror_path = base_path + 'mirror/'
subversion_path = mirror_path + 'subversion/'
downloads_path = mirror_path + 'downloads/'
repositories_path = mirror_path + 'repositories/'

# Project Lists
directories = [ d for d in os.listdir( path ) if os.path.isdir( os.path.join( path, d ) ) ]
directories_count = sum( [ len( directories ) ] )
projects_with_subversion = []
projects_with_downloads = []
projects = []


#
# Excludes
#

# Project Subversion Repository Excludes
exclude_subversion = [ '_', '30_second_timeout_remedy', '_http_', 'share', 'social', 'xajax', 'var', 'user', 'cie', 'bc', 'ciet', 'cmsxf2b', 'download', 'extension', 'ezcommunityopml', 'ezecosystem', 'ezauthorize', 'ezcurlgateway', 'ezjscore', 'ezpedia', 'ezsdk', 'manuals', 'membership', 'batchtool', 'bdbashcompletion', 'ezdbug', 'opensearch', 'ezgpg', 'ezoe2', 'ezpublish_translation_fre_fr', 'ez_cache_manager', 'cossi_pxml', 'ezjscore2', 'membership2', 'owner2', 'redirect2', 'soextra', 'ezless', 'swark', 'swark_for_ez_publish_4', 'all2egooglesitemaps', 'cjw_newsletter', 'dappsocial', 'ezdevtools', 'ezrestdebugger', 'eztags', 'jvlogout', 'less_css', 'ngcomments', 'ngconnect', 'ngindexer', 'nl_cronjobs', 'nxc_captcha', 'nxc_extendedfilter', 'nxc_hotkeys', 'owsimpleoperator', 'owsortoperator', 'phpids', 'qhjsiniloader', 'qhnotifications', 'remoting', 'remoting', 'strip_except', 'swark', 'swark_for_ez_publish_4', 'textmate_bundle_for_ez_template_and_ini_files', 'unofficialhabla', 'updatesearchindex', 'wrap_operator', 'yubico_yubikey_otp_extension_for_ez_publish', 'ezfluxbb', 'ezplanet', 'eztags', 'eztidy', 'ezurlfilterchinese', 'nmcontentclass', 'objectrelationbrowse', 'types', 'content', 'membership__1' ]

# Project Download Excludes
exclude_downloads = [ '_', '30_second_timeout_remedy', '_http_', 'share', 'social', 'xajax', 'var', 'user', 'bc', 'download', 'extension', 'ezcommunityopml', 'ezecosystem', 'ezjscore', 'ezpedia', 'ezsdk', 'manuals', 'membership', 'batchtool', 'bdbashcompletion', 'ezdbug', 'opensearch', 'ezgpg', 'ezoe2', 'all2egooglesitemaps', 'eztags', 'ngcomments', 'ngconnect', 'ngindexer', 'nl_cronjobs', 'nxc_captcha', 'nxc_extendedfilter', 'nxc_hotkeys', 'remoting', 'textmate_bundle_for_ez_template_and_ini_files', 'updatesearchindex', 'types', 'content', 'membership__1' ]


#
# Function Definitions
#

# Calls to GitHub
def github_call(url, token, data):
    headers = {'Authorization' : 'token ' + token}
    result = requests.post(url, data=data, headers=headers)
    return result

# Connect to GitHub
def connect_to_github( token ):
    try:
        github = Github( token )
        user = github.get_user()
        if verbose:
            print( "Connection to GitHub Established!" )
        return github
    except NameError:
        print( "Connection to GitHub Failed!" )
        return False

# Test if path contains git repository
def is_git_repo( path ):
    try:
        _ = git.Repo( path ).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False

# Test if local git repository (from remote clone) is an empty repository
def is_repo_empty( url, name, repositories_path, verbose=False, debug_level=0 ):
     bare = False
     rpath = repositories_path + name
     Repo.clone_from( url, rpath )
     # bare = git.Repo( rpath ).working_tree_dir
     rpath_files = os.listdir( rpath )
     rpath_files.remove( '.git' )
     if verbose and debug_level >= 1:
         print( "Repository contents: " )
         print( rpath_files )
     if not rpath_files:
         bare = True
     if verbose and debug_level >= 1:
         print( "Remote repository empty: " + str( bare ) )
     return bare

# Delete all repositories
def delete_repositories( directories, github_connection, delete_only=False, limit=7500, order=False, verbose=False, debug_level=0 ):
    if delete_only == True:
        print( "Removing all repositories ..." )
        if order == 'reverse':
            dictionaries_ordered = reversed( sorted( directories ) )
        else:
            dictionaries_ordered = sorted( directories )
        for( name ) in dictionaries_ordered[:limit]:
            try:
                user = github_connection.get_user()
                repository = user.get_repo( name )
                if repository.delete() == None:
                    print( "Repository removed: " + name )
            except github.GithubException:
                if verbose and debug_level >= 0:
                    print "Repository did not exist and removal failed: " + name
                pass
        if verbose and debug_level >= 0:
            print( "All repository removal completed" )
        quit()

# Delete empty repositories
def delete_empty_repositories( directories, github_connection, delete_empty_repos=False, repositories_path='/tmp/projects/repositories/', limit=7500, order=False, verbose=False, debug_level=0 ):
    if delete_empty_repos:
        print( "Removing empty repositories only ..." )
        if order == 'reverse':
            dictionaries_ordered = reversed( sorted( directories ) )
        else:
            dictionaries_ordered = sorted( directories )
        for( name ) in dictionaries_ordered[:limit]:
            try:
                user = github_connection.get_user()
                repository = user.get_repo( name )
                if verbose and debug_level >= 1:
                    print( "Evaluating repository: " + name )
                if is_repo_empty( repository.clone_url, name, repositories_path, verbose, debug_level ):
                    if repository.delete() == None:
                        print( "Empty repository removed: " + name )
                else:
                    print( "Repository not empty: " + name )
            except github.GithubException:
                if verbose and debug_level >= 0:
                    print "Empty repository did not exist and removal failed: " + name
                pass
        if verbose and debug_level >= 0:
            print( "Empty repository removal completed" )
        quit()

# Process all subversion project repositories
def process_project_repositories( projects_with_subversion, github_connection, subversion_only=False, subversion_path='/tmp/mirror/subversion/', path='/tmp/mirror/', base_path='/tmp/', subversion_import=False, exclude_subversion=[], delete_empty_repos=False, log_only=False, local=True, limit=7500, git_account='ezpublishlegacyprojects', repository_hostname='github.com', verbose=False, debug_level=0 ):
    if subversion_only:
        for ( project ) in projects_with_subversion[:limit]:
            name = str( project )
            repo_name = name 
            project_url = "http://projects.ez.no/" + name
            project_svn_url = "http://svn.projects.ez.no/" + name
            repo_path = subversion_path + '/' + name + '/'
            if "bc" not in name and name not in exclude_subversion and subversion_only:
                print( "Project: " + name )
                # print( "Project Authors: ")
                # os.system( 'svn log --quiet http://svn.projects.ez.no/' + name + ' | grep -E "r[0-9]+ \| .+ \|" | cut -d"|" -f2 | sed "s/ //g" | sort | uniq' )
                print( " " )
                if not log_only:
                    try:
                        user = github_connection.get_user()
                        repository = user.get_repo( name )
                        try:
                            repository.name
                            if verbose:
                                print("Repository Exists: " + repository.name )
                                print("Skipping Repository Creation ..")
                            # Import subversion repository content
                            import_subversion_repository( repository, name, repo_name, project_svn_url, delete_empty_repos, local, subversion_path, path, repo_path, base_path, subversion_import, repository_hostname, git_account, verbose, debug_level )
                        except NameError:
                            pass #print "Repository did not exist or could not be accessed"
                    #else:
                        #if verbose:
                        #    print("Repository Exists: " + name )
                        #    print("Skipping Repository Creation")
                    except github.GithubException as e:
                        # print e, e.request, e.response
                        if "bc" not in name:
                            if local:
                                print( "GitHub Repository Missing: " + name )
                                print( "Creating repository ..." )
                                repository = user.create_repo( name, project_url, project_url, False, True, True, True ) 

                                if repository:
                                    print( "Created {0} successfully!" . format( repository.name ) )
                            else:
                                repository = False

                            # Import subversion repository content
                            import_subversion_repository( repository, name, repo_name, project_svn_url, delete_empty_repos, local, subversion_path, path, repo_path, base_path, subversion_import, repository_hostname, git_account, verbose, debug_level )

                else:
                    if not verbose:
                        print( "Skipping repository: " + name )

# Process all project downloads
def process_project_downloads( projects_with_downloads, github_connection, download_only, subversion_path, path, base_path, download_import, exclude_downloads=[], delete_empty_repos=False, log_only=False, local=True, limit=7500, git_account='ezpublishlegacyprojects', repository_hostname='github.com', verbose=False, debug_level=0 ):
    if download_only == True:
        for ( project ) in projects_with_downloads[:limit]:
        # for ( project ) in [ 'membership2' ]:
            name = str( project )
            repo_name = name + '_downloads'
            project_url = "http://projects.ez.no/" + name
            repo_path = downloads_path + repo_name + '/'
            if "bc" not in name and name not in exclude_downloads and download_only:
                print( "Project: " + name )
                print( "Repo Name: " + repo_name )
                print( " " )
                if log_only == False:
                    try:
                        user = github_connection.get_user()
                        repository = user.get_repo( repo_name )

                        try:
                            repository.name
                            if verbose:
                                print("Repository Exists: " + repository.name )
                                print("Skipping Repository Creation ..")

                            import_downloads( repository, name, repo_name, project_url, delete_empty_repos, local, downloads_path, path, repo_path, base_path, download_import, repository_hostname, git_account, verbose, debug_level )

                        except NameError:
                            print "Repository did not exist: " + repo_name
                        #else:
                            #if verbose:
                            #    print("Repository Exists: " + name )
                            #    print("Skipping Repository Creation")
                    except github.GithubException as e:
                        # print e, e.request, e.response
                        if "bc" not in name:
                            if local:
                                print( "GitHub Repository Missing: " + repo_name )
                                print( "Creating repository ..." )
                                repository = user.create_repo( repo_name, project_url, project_url, False, True, True, True ) 

                                if repository:
                                    print("Created {0} successfully!" . format( repository.name ) )
                            else:
                                repository = False

                            # Import downloads repository content
                            import_downloads( repository, name, repo_name, project_url, delete_empty_repos, local, downloads_path, path, repo_path, base_path, download_import, repository_hostname, git_account, verbose, debug_level )

            else:
                print( "Skipping repository: " + name )

# Import project downloads into repository
def import_downloads( repository=False, name=False, repo_name=False, project_url=False, delete_empty_repos=False, local=True, downloads_path='/tmp/mirror/downloads', path='/tmp/mirror/', repo_path='/tmp/mirror/repositories', base_path='/tmp/projects', downloads_import=False, repository_hostname='github.com', git_account='ezpublishlegacyprojects', verbose=False, debug_level=0 ):
    if os.path.exists( repo_path ):
        if download_import == True:
            os.chdir( downloads_path )
            print( "Importing raw downloads into repository" );
            os.system( 'git init ' + repo_path )
            os.chdir( path )
            os.system( "find " + path + name + "/downloads -name '*.html' -exec cat {} \;| egrep -o 'href=\"(.*?)\/content\/download\/[0-9]+\/[0-9]+\/version\/[0-9]+\/file\/(.*?)\"' | sed 's/^href=\"..\/..\/..\///' | sed 's/^href=\"..\/..\///' | sed 's/\"//' | python -c \"import sys, urllib as ul; urls=ul.unquote( sys.stdin.read() ).decode('utf8').rstrip().split('\\n'); sys.stdout.write('rsync -va --backup --suffix=$(date +\"_%s\")'); [ sys.stdout.write(' \\\"" + path + "' + item_path + '\\\"') for item_path in urls ]; sys.stdout.write(' \\\"" + repo_path + "\\\"' ); \" | sh" )
            os.chdir( repo_path )
            os.system( "git add *" )
            os.system( "git commit -m\"Added: Imported projects.ez.no project download archives, renamed to fit in same directory in an automated manner\" ." )
            os.system( 'pwd' )
            os.system( 'git remote add github git@' + repository_hostname + ':' + git_account + '/' + name + '.git' )
        if local:
            os.chdir( repo_path )
            if verbose and debug_level >= 1:
                os.system( 'pwd' )
            os.system( 'git remote rm github' )
            os.system( 'git remote add github git@' + repository_hostname + ':' + git_account + '/' + repo_name + '.git' )
            os.system( 'git push --all github' )
            if repository != False and is_repo_empty( repository.clone_url, repo_name, repositories_path, verbose, debug_level ) and delete_empty_repos:
                if repository.delete() == None:
                    print( "Deleted empty repository: " + repo_name )
            os.chdir( base_path )
            print( " " )
    else:
        if download_import:
            os.chdir( downloads_path )
            print( "Importing raw downloads into repository" );
            os.system( 'git init ' + repo_path )
            os.chdir( path )
            os.system( "find " + path + name + "/downloads -name '*.html' -exec cat {} \;| egrep -o 'href=\"(.*?)\/content\/download\/[0-9]+\/[0-9]+\/version\/[0-9]+\/file\/(.*?)\"' | sed 's/^href=\"..\/..\/..\///' | sed 's/^href=\"..\/..\///' | sed 's/\"//' | python -c \"import sys, urllib as ul; urls=ul.unquote( sys.stdin.read() ).decode('utf8').rstrip().split('\\n'); sys.stdout.write('rsync -va --backup --suffix=$(date +\"_%s\")'); [ sys.stdout.write(' \\\"" + path + "' + item_path + '\\\"') for item_path in urls ]; sys.stdout.write(' \\\"" + repo_path + "\\\"' ); \" | sh" )
            os.chdir( repo_path )
            os.system( "git add *" )
            os.system( "git commit -m\"Added: Imported projects.ez.no project download archives, renamed to fit in same directory in an automated manner\" ." )
            os.system( 'pwd' )
            os.system( 'git remote add github git@' + repository_hostname + ':' + git_account + '/' + name + '.git' )
        if local:
            os.chdir( repo_path )
            if verbose and debug_level >= 1:
                os.system( 'pwd' )
            os.system( 'git remote rm github' )
            os.system( 'git remote add github git@' + repository_hostname + ':' + git_account + '/' + repo_name + '.git' )
            os.system( 'git push --all github ' )
            if repository != False and is_repo_empty( repository.clone_url, repo_name, repositories_path, verbose, debug_level ) and delete_empty_repos:
                if repository.delete() == None:
                    print( "Deleted empty repository: " + repo_name )
            os.chdir( base_path )
            print( " " )

# Import subversion repository content
def import_subversion_repository( repository=False, name=False, repo_name=False, project_svn_url=False, delete_empty_repos=False, local=True, subversion_path='/tmp/mirror/subversion', path='/tmp/mirror/', repo_path='/tmp/mirror/repositories', base_path='/tmp/projects', subversion_import=False, repository_hostname='github.com', git_account='ezpublishlegacyprojects', verbose=False, debug_level=0 ):
    if os.path.exists( repo_path ):
        if subversion_import:
            os.chdir( subversion_path )
            print( "Importing raw svn repository history" );
            os.system( 'git svn clone --prefix='' --authors-file=/home/brookins/.svn2git/authors --trunk=/ ' + project_svn_url + ' --tags=/tags/ --branches=/branches/' )
            os.chdir( repo_path )
            os.system( 'pwd' )
            os.system( 'git remote add github git@' + repository_hostname + ':' + git_account + '/' + repo_name + '.git' )
        if local:
            os.chdir( repo_path )
            os.system( 'git push --all github' )
            if repository != False and is_repo_empty( repository.clone_url, repo_name, repositories_path, verbose, debug_level ) and delete_empty_repos:
                if repository.delete() == None:
                    print( "Deleted empty repository: " + repo_name )
            os.chdir( base_path )
            print( " " )
    else:
        if subversion_import:
            os.chdir( subversion_path )
            print( "Importing raw svn repository history" );
            os.system( 'git svn clone --prefix='' --authors-file=/home/brookins/.svn2git/authors --trunk=/ ' + project_svn_url + ' --tags=/tags/ --branches=/branches/' )
            os.chdir( repo_path )
            os.system( 'pwd' )
            os.system( 'git remote add github git@' + repository_hostname + ':' + git_account + '/' + repo_name + '.git' )
        if local:
            os.chdir( repo_path )
            os.system( 'git push --all github ' )
            if repository != False and is_repo_empty( repository.clone_url, repo_name, repositories_path, verbose, debug_level ) and delete_empty_repos:
                if repository.delete() == None:
                    print( "Deleted empty repository: " + repo_name )
            os.chdir( base_path )
            print( " " )

# Display project names and exit
def debug_exit_print( projects ):
    print projects
    quit()

# Calculate subversion and download projects from directories list
def calculate_projects( directories ):
    for ( subdirname ) in sorted( directories ):
        dirpath = os.path.join( path, subdirname )
        if subdirname not in exclude_subversion and os.path.isfile( dirpath + '.html' ):
            projects.append( subdirname )
            if subdirname not in exclude_subversion and os.path.isdir( dirpath + '/subversion' ):
                projects_with_subversion.append( subdirname )
            else:
                if os.path.isdir( dirpath + '/downloads' ) and subdirname not in exclude_subversion and subdirname not in projects_with_subversion and "bc" not in subdirname:
                    projects_with_downloads.append( subdirname )

# Display detected project totals (initial program output)
def print_detection_totals( projects, projects_with_downloads, projects_with_subversion, verbose=False, debug_level=0 ):
    if verbose and debug_level >= 1:
        print("Detected total projects: " + str( sum( [ len( projects ) ] ) ) )
        print("Detected download projects: " + str( sum( [ len( projects_with_downloads ) ] ) ) )
        print("Detected subversion projects: " + str( sum( [ len( projects_with_subversion ) ] ) ) )


#
# Begin Main Program
#

# Calculate projects
calculate_projects( directories )

# Display project totals
print_detection_totals( projects, projects_with_downloads, projects_with_subversion, verbose, debug_level )

# Debug : Display projects
if debug_exit_print_subversion:
    debug_exit_print( projects_with_subversion )
elif debug_exit_print_downloads:
    debug_exit_print( projects_with_downloads )
elif debug_exit_print_directories:
    debug_exit_print( directories )


# Connect to GitHub
github_connection = connect_to_github( token )

# Remove all empty repositories
delete_empty_repositories( directories, github_connection, delete_empty_repos, repositories_path, limit, order, verbose, debug_level )

# Remove all repositories
delete_repositories( directories, github_connection, delete_only, limit, order, verbose, debug_level )

# Process all project repositories
process_project_repositories( projects_with_subversion, github_connection, subversion_only, subversion_path, path, base_path, subversion_import, exclude_subversion, delete_empty_repos, log_only, local, limit, account, repository_hostname, verbose, debug_level )

# Process all project downloads
process_project_downloads( projects_with_downloads, github_connection, download_only, subversion_path, path, base_path, download_import, exclude_downloads, delete_empty_repos, log_only, local, limit, account, repository_hostname, verbose, debug_level )

# fin
quit()
