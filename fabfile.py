from fabric.api import env, run
from fabric.context_managers import cd
from fabric.operations import sudo, put
from fabric.contrib.files import exists


def vagrant():
    env.hosts = ['192.168.33.103']
    env.user = 'vagrant'
    env.password = 'vagrant'


def ocean():
    env.hosts = ['104.236.51.225']
    env.user = 'sean'


def testing():
    run('ls')


def tail():
    sudo('tail -f /var/log/uwsgi/app/compositron.log')


def install():
    link_confs('compositron', 'compositron')
    create_env('compositron')
    install_pip_reqs()
    restart()


def build3():
    apt_update()
    add_apt_repo()
    create_log_dirs()
    apt_update()
    install_nginx()
    install_uwsgi()
    install_python()
    install_git()
    link_confs('compositron', 'compositron')
    create_env('compositron')
    install_pip_reqs()
    restart()


def build():
    apt_update()
    add_apt_repo()
    create_log_dirs()
    apt_update()
    install_nginx()
    install_uwsgi()
    install_python()
    install_git()
    # mysql_install()
    # create_mysql_db()
    # create_mysql_user()
    create_env()
    upgrade_distribute()
    install_pip_reqs()
    link_confs()
    fix_la()
    restart()


def make_directory(dir_name='msma'):
    with cd('/srv/'):
        if not exists(dir_name):
            sudo('mkdir {}'.format(dir_name))
            sudo('chown {}:{} {}'.format(env.user, dir_name))


def git_clone_repo(dir_name='msma'):
    repo = 'git@bitbucket.org:joshue/1127_server.git'
    with cd('/srv/'):
        sudo('git clone {} {}'.format(repo, dir_name))


def create_env(venv='compositron'):
    run('cd /home/{}'.format(env.user))
    run('python3 -m venv {}'.format(venv))


def upgrade_distribute(venv='msma_env'):
    #sudo('easy_install -U distribute')
    command = '/home/{}/{}/bin/pip install --upgrade distribute'
    run(command.format(env.user, venv))


def install_pip_reqs(venv='compositron'):
    command = '/home/{0}/{1}/bin/pip install --upgrade -r ' \
              '/srv/{1}/{1}/requirements.txt'
    run(command.format(env.user, venv))


def link_confs(dir_name='compositron', file_name='compositron'):
    n1 = 'ln -s /srv/{0}/{0}/confs/{1} /etc/nginx/sites-available/{1}'
    sudo(n1.format(dir_name, file_name))
    u1 = 'ln -s /srv/{0}/{0}/confs/{1}.ini /etc/uwsgi/apps-available/{1}.ini'
    sudo(u1.format(dir_name, file_name))
    n2 = 'ln -s /etc/nginx/sites-available/{0} /etc/nginx/sites-enabled/{0}'
    sudo(n2.format(file_name))
    u2 = 'ln -s /etc/uwsgi/apps-available/{0}.ini ' \
         '/etc/uwsgi/apps-enabled/{0}.ini'
    sudo(u2.format(file_name))


def create_log_dirs():
    sudo('mkdir -p /var/www/logs')
    sudo('touch /var/www/logs/error.log')
    sudo('touch /var/www/logs/access.log')
    sudo('chown -R www-data:www-data /var/www')


def fix_la():
    run("sed -i \"/alias la='ls -A'/c\ alias la='ls -lAh'\" /home/{}/.bashrc")


def restart():
    sudo('service nginx restart')
    sudo('service uwsgi restart')


def deploy():
    with cd('/srv/compositron'):
        if env.user == 'compositron':
            run('git pull')
            run('git submodule foreach git checkout master')
            run('git submodule foreach git pull origin master')
        command = '/home/{}/msma_env/bin/pip install -r msma/requirements.txt'
        run(command.format(env.user))
        run('/home/{}/msma_env/bin/python manage.py migrate'.format(env.user))
    restart()


### apt-get stuff ###


def add_apt_repo():
    sudo('apt-get install python3-software-properties')


def apt_update():
    sudo('apt-get update')


### ssh key stuff ###


def ssh_setup():
    if not exists('~/.ssh/'):
        print "--ssh directory doesnt exist.  creating"
        run('mkdir ~/.ssh')
    if exists('~/.ssh/id_rsa.pub') or exists('~/.ssh/id_rsa'):
        print "--keys exist.  bail"
    else:
        print "--keys dont exist.  copying local keys for github access"
        put('~/.ssh/id_rsa*', '~/.ssh/')
    run('chmod 600 ~/.ssh/id_rsa')


### installs ###


def install_nginx():
    sudo('apt-get install nginx-full')


def install_uwsgi():
    sudo('apt-get install uwsgi uwsgi-plugin-python3')


def install_python():
    sudo('apt-get install python3-setuptools')
    sudo('apt-get install python3.4-venv')
    sudo('apt-get install python3-dev')
    sudo('apt-get install build-essential')


def install_git():
    run('sudo apt-get install git')


def check_for_bin():
    run('cd ~')
    if not exists('bin'):
        print "directory doesn't exist.  creating"
        run('mkdir bin')
    thepath = run('echo $PATH')
    currentdir = run('pwd')
    dir_components = currentdir.split('/')
    filter(None, dir_components)
    dir_components.append('bin')
    newdir = '/'.join(dir_components)
    if newdir not in thepath:
        run('echo PATH=$PATH:{} >> .profile'.format(currentdir))


def install_emacs24():
    sudo('add-apt-repository ppa:cassou/emacs')
    apt_update()
    sudo('apt-get install emacs24 emacs24-el emacs24-common-non-dfsg')


def install_twisted():
    #sudo('add-apt-repository ppa:twisted-dev/ppa')
    #apt_update()
    sudo('apt-get install python-twisted')


def install_node():
    sudo('add-apt-repository ppa:chris-lea/node.js')
    sudo('apt-get update')
    sudo('apt-get install python g++ make nodejs')


def install_mongodb():
    sudo('apt-key adv --keyserver '
         'hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10')
    run("echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart "
        "dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list")


def install_mysql():
    sudo('apt-get install mysql-server mysql-client')
    sudo('apt-get install libmysqlclient-dev')


def create_mysql_db(password=None):
    user = 'root'
    dbname = 'msma'
    if password:
        run('mysqladmin -u {} -p{} create {}'.format(user, password, dbname))
    else:
        run('mysqladmin -u {} create {}'.format(user, dbname))


def create_django_tables():
    command = '/home/{}/msma_env/bin/python /srv/msma/manage.py syncdb'
    run(command.format(env.user))


def apt_get(*packages):
    sudo('apt-get -y --no-upgrade install %s' % ' '.join(packages),
         shell=False)
