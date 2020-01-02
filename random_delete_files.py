import random, os
from shutil import copy2

data_dir = 'ML useful/Face recognition/UTKFace/dataset/Young adult'


def random_rm_from_folder():
    filenames = random.sample(os.listdir(data_dir), 20)
    random.shuffle(filenames)
    random.shuffle(filenames)
    for fname in filenames:
        srcpath = os.path.join(data_dir, fname)
        os.remove(srcpath)


def random_cp_to_folder():
    filenames = random.sample(os.listdir(data_dir + "/All"), 500)
    for fname in filenames:
        srcpath = os.path.join(data_dir + "/All", fname)
        copy2(srcpath, data_dir + "/UTKFace/People/")


def del_identical():
    folders = os.listdir(data_dir)
    folder_len = len(folders)

    for i in range(folder_len):
        folder1 = folders[i]

        for l in range(i + 1, folder_len):
            folder2 = folders[l]

            files1 = os.listdir(os.path.join(data_dir, folder1))
            files2 = os.listdir(os.path.join(data_dir, folder2))

            for fname1 in files1:
                for fname2 in files2:
                    if fname1 == fname2:
                        srcpath = os.path.join(data_dir, folder2, fname2)
                        os.remove(srcpath)