#!/usr/bin/env python
import os
import sys


def echo(msg=''):
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()


def fail(msg):
    sys.stderr.write(msg + '\n')
    sys.stderr.flush()
    sys.exit(1)


def succeed(msg):
    echo(msg)
    sys.exit(0)


def main():
    if len(sys.argv) == 3:
        home_dir = os.path.expanduser(sys.argv[1])
        bin_dir = os.path.expanduser(sys.argv[2])
        custom_dirs = True
    else:
        bin_dir = os.path.expanduser('~/.local/bin')
        home_dir = os.path.expanduser('~/.local/venvs')
        custom_dirs = False

    print('Installing pipsi [home_dir={}, bin_dir={}]'.format(home_dir, bin_dir))

    if os.name != 'posix':
        fail('So sorry, but pipsi only works on POSIX systems :(')

    if os.system('pipsi --version >/dev/null 2>/dev/null') == 0:
        succeed('You already have pipsi installed')

    if os.system('virtualenv --version >/dev/null 2>/dev/null') != 0:
        fail('You need to have virtualenv installed to bootstrap pipsi.')

    try:
        os.makedirs(bin_dir)
        os.makedirs(home_dir)
    except OSError:
        pass

    import shutil
    from subprocess import Popen
    venv = os.path.join(home_dir, 'pipsi')

    def _cleanup():
        try:
            shutil.rmtree(venv)
        except (OSError, IOError):
            pass

    if Popen(['virtualenv', venv]).wait() != 0:
        _cleanup()
        fail('Could not create virtualenv for pipsi :(')

    if Popen([venv + '/bin/pip', 'install', 'pipsi']).wait() != 0:
        _cleanup()
        fail('Could not install pipsi :(')

    os.symlink(venv + '/bin/pipsi', bin_dir + '/pipsi')

    if custom_dirs:
        config  = "[pipsi]\n"
        config += "home = {}\n".format(home_dir)
        config += "bin_dir = {}\n".format(bin_dir)
        with open(os.path.expanduser('~/.pipsirc'), 'w') as f:
            f.write(config)

    if os.system('pipsi --version >/dev/null 2>/dev/null') != 0:
        echo()
        echo('=' * 60)
        echo()
        echo('Warning:')
        echo('  It looks like %s is not on your PATH so pipsi will' % bin_dir)
        echo('  not work out of the box.  To fix this problem make sure to')
        echo('  add this to your .bashrc / .profile file:')
        echo()
        echo('  export PATH=%s:$PATH' % bin_dir)
        echo()
        echo('=' * 60)
        echo()

    succeed('pipsi is now installed.')


if __name__ == '__main__':
    main()
