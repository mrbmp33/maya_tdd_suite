import pathlib
import sys


def find_importable_root(path):
    directory = pathlib.Path(path)
    module = list(directory.glob("*.py"))[0]

    for each in module.parents:
        if '__init__.py' not in [x.name for x in each.iterdir() if x.is_file()]:
            return str(each)


if __name__ == '__main__':
    p = find_importable_root(r'/home/bernat/Dades/Documents/01_personal_projects/FKSolver/fks/tests')
    if p not in sys.path:
        print(p)
        sys.path.insert(0, p)

    import fks.tests.test_weakDataObjects
