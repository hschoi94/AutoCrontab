import tarfile
import re
import os

not_pariod_tag = "0"

def mk_period(year=0, month=0, day=0, hour=0, minute=0, sec=0):
    # file name: YYYY_MM_DD_hh_mm_ss-filename
    # then scheduling YYYYMMDDhhmmss period
    # else working ASAP
    day = day + month * 30 + year * 365
    return "{}_{}_{}_{}".format(day, hour, minute, sec)


def split_file_name(file_name):
    dash_index = [pos for pos, char in enumerate(file_name) if char == "-"]
    name = file_name[dash_index[1] + 1 :]
    period = file_name[dash_index[0] + 1 : dash_index[1]]
    work = file_name[: dash_index[0]]
    return work, period, name


def mk_file_name(
    file_name, year=0, month=0, day=0, hour=0, minute=0, sec=0, background=False
):
    if year + month + day + hour + minute + sec != 0:
        period_string = mk_period(year, month, day, hour, minute, sec)
    else:
        period_string = "0"

    if background:
        work = "B"  # background
    else:
        work = "F"  # forground

    return "{}-{}-{}".format(work, period_string, file_name)


def get_period(file_name):
    # return period_string
    return split_file_name(file_name)[1]


def get_ground_dirction(file_name):
    # return year, month, day, hour, minute, sec string
    if split_file_name(file_name)[0] == "B":
        return "Background"
    else:
        return "Forground"


def get_dirlist(dir_path, ignore_list):
    if os.path.isdir(dir_path):
        file_list = os.listdir(dir_path)
        res_list = []
        for f in file_list:
            ignore_flag = False
            for i in ignore_list:
                p = re.compile(ignore_list[i])
                if p.match(f):
                    ignore_flag = True
                    break

            if ignore_flag is False:
                res_list.append(f)
        return res_list
    else:
        print("No such dir")
        return []


def gen_tarfile(tarfile_path, dir_path, ignore_file_path=None):
    if ignore_file_path is None:
        ignore_list = []
    else:
        ignore_list = []
    file_list = get_dirlist(dir_path, ignore_list)
    now_path = os.getcwd()
    if len(file_list) > 0:
        with tarfile.open(tarfile_path, "w") as mytar:
            os.chdir(dir_path)
            for f in file_list:
                mytar.add(f)
    os.chdir(now_path)


if __name__ == "__main__":
    tarfile_path = "./name"
    dir_path = "./dir_path"
    ignore_file_path = "./ignore_file_path"
    file_name = mk_file_name("test9", sec=0) + ".tar"
    code_path = os.path.dirname(__file__)
    gen_tarfile("./" + file_name, os.path.join(code_path, "test"))
    # gen_tarfile(tarfile_path, dir_path, ignore_file_path)
