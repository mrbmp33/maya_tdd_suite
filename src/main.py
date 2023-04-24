import argparse
import os


def main():
    parser = argparse.ArgumentParser(description='Runs unit tests for a Maya module')
    parser.add_argument('-m', '--maya',
                        help='Maya version',
                        type=int,
                        default=2022)
    parsed_args = parser.parse_args()
    mayaunittest = os.path.join(CMT_ROOT_DIR, 'scripts', 'cmt', 'test', 'mayaunittest.py')
    cmd = [mayapy(parsed_args.maya), mayaunittest]
    if not os.path.exists(cmd[0]):
        raise RuntimeError('Maya {0} is not installed on this system.'.format(parsed_args.maya))
    
    maya_app_dir = create_clean_maya_app_dir()
    # Create clean prefs
    os.environ['MAYA_APP_DIR'] = maya_app_dir
    # Clear out any MAYA_SCRIPT_PATH value so we know we're in a clean env.
    os.environ['MAYA_SCRIPT_PATH'] = ''
    # Run the tests in this module.
    os.environ['MAYA_MODULE_PATH'] = CMT_ROOT_DIR
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        pass
    finally:
        shutil.rmtree(maya_app_dir)


if __name__ == '__main__':
    main()
