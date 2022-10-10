import os
from multiprocessing import Process
import time
import tarfile
import shutil
import datetime
import global_config as global_config
from global_config import run_file
from gen_tarfile import get_period, not_pariod_tag


def init_path_gen(root_path_dict):
    keys = root_path_dict.keys()
    for key in keys:
        path = root_path_dict[key]
        if os.path.exists(path) is False:
            os.mkdir(path)

    return root_path_dict


def mkdir(path):
    if os.path.exists(path) is False:
        os.mkdir(path)
    return path


def get_now_time():
    current_time = datetime.datetime.now()
    time_stemp = current_time.strftime("%Y_%m_%d_%H_%M_%S")
    return time_stemp


def delta2sec(delta_time):
    date = delta_time.days
    sec = date * 24 * 3600 + delta_time.seconds
    return sec


def get_dirs(dir_path):
    tmp = []
    dir_list = os.listdir(dir_path)
    for dir_ in dir_list:
        dir_path = os.path.join(dir_path, dir_)
        if os.path.isdir(dir_path):
            tmp.append(dir_path)
    return tmp


def get_files(file_path, types):
    if len(types) > 0:
        tar_files = [
            pos for pos in os.listdir(file_path) if os.path.splitext(pos)[1] in types
        ]
    else:
        tar_files = [pos for pos in os.listdir(file_path)]
    return tar_files


def get_time_att(string):
    dash_index = [pos for pos, char in enumerate(string) if char == "-"]
    return string[dash_index[-1] + 1 :]


def get_time(string):
    if string[-1:] == "\n":
        string = string[:-1]
    time = get_time_att(string)
    return datetime.datetime.strptime(time, "%Y_%m_%d_%H_%M_%S")


def get_period2delta(period):
    day, hour, minute, sec = period
    p_time = datetime.timedelta(
        days=int(day),
        hours=int(hour),
        minutes=int(minute),
        seconds=int(sec),
    )
    return p_time


class Schedule(Process):
    def __init__(self, input_dir, exec_dir, backup_dir):
        super(Process, self).__init__()
        self.exec_dir = exec_dir
        self.input_dir = input_dir
        self.backup_dir = backup_dir
        self.log_path = mkdir(os.path.join(self.exec_dir, "log"))

        self.file_name = os.path.basename(self.exec_dir)
        self.new_input_path = os.path.join(input_dir, self.file_name + ".tar")
        period = get_period(self.file_name)
        self.sleep_time = get_period2delta(period)

        self.get_last_run()
        self.exit_flag = False
        self.last_run_time = "init"
        print(self.last_run_time)

    def get_last_run(self):
        log_files = os.listdir(self.log_path)
        tmp = []
        for log_file in log_files:
            log_name, ext = os.path.splitext(log_file)
            if ext == ".log":
                tmp.append(log_name)

        if len(tmp) > 0:
            time = get_time(tmp[0])
            tmp = tmp[1:]
            for file_name in tmp:
                g_time = get_time(file_name)
                if g_time > time:
                    time = g_time

            self.last_run_time = time.strftime("%Y_%m_%d_%H_%M_%S")

    def get_next_time(self):
        if os.path.exists(self.new_input_path):
            self.end_backup()
        return self.sleep_time + datetime.datetime.now()

    def end_backup(self):
        backup_path = os.path.join(
            self.backup_dir, "{}-B{}".format(self.file_name, get_now_time())
        )
        shutil.move(self.new_input_path, backup_path)

    def check_state(self):
        if self.last_run_time != "init":
            period = get_period(self.file_name)
            if period == not_pariod_tag or self.exit_flag:
                self.end_backup()
                return False
            plan_time = self.get_next_time()
            if datetime.datetime.now() > plan_time:
                return True
            else:
                time.sleep(delta2sec(self.sleep_time))
                return True
        else:
            return True

    def exec_files(self):
        exec_run_file_path = os.path.join(self.exec_dir, run_file)
        dir_name = os.path.basename(self.exec_dir)
        log_file_path = os.path.join(self.log_path, "{}.log".format(dir_name))

        if os.path.isfile(exec_run_file_path):
            os.system("bash {} > {}".format(exec_run_file_path, log_file_path))
        else:
            os.system(
                "echo 'Error: not exec file {} in {}' > {}".format(
                    run_file, self.exec_dir, log_file_path
                )
            )
            self.exit_flag = True
        self.last_run_time = get_now_time()
        log_result_path = os.path.join(
            self.log_path, "{}-{}.log".format(dir_name, self.last_run_time)
        )
        shutil.move(log_file_path, log_result_path)

    def run(self):
        while self.check_state():
            self.exec_files()


class WorkspaceManager:
    def __init__(self, input_tar_dir, workspace_dir):
        self.workspace_dir = workspace_dir
        self.input_tar_dir = input_tar_dir
        self.types = [".tar"]
        self.works = []
        self.new_works = []

    def regist_new_schedule(self, backup_path):
        self.get_new_works()
        self.get_works()
        tmp = []
        works_fn = get_dirs(self.workspace_dir)
        for new_work in self.new_works:
            file_name = os.path.basename(os.path.splitext(new_work)[0])
            if file_name not in works_fn:
                tar_file_path = os.path.join(self.input_tar_dir, file_name + ".tar")
                ap = tarfile.open(tar_file_path)
                ext_path = mkdir(os.path.join(self.workspace_dir, file_name))
                ap.extractall(ext_path)
                ap.close()
                mv_file_path = os.path.join(
                    backup_path, "{}-{}.tar".format(file_name, get_now_time())
                )
                shutil.move(tar_file_path, mv_file_path)
                tmp.append(file_name)
            else:
                print("{} is already in workspace".format(file_name))
        return tmp

    def get_works(self):
        self.works = get_dirs(self.workspace_dir)
        return len(self.works)

    def get_new_works(self):
        self.new_works = get_files(self.input_tar_dir, self.types)
        return len(self.new_works)


if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path_dic = init_path_gen(global_config.use_paths(dir_path))
    workspace_m = WorkspaceManager(
        input_tar_dir=path_dic["input"], workspace_dir=path_dic["workspace"]
    )
    print(workspace_m.regist_new_schedule(path_dic["backup"]))

    works = get_dirs(path_dic["workspace"])
    print(works)
    process = []

    process_flag = True
    while process_flag:
        for work in works:
            p = Schedule(
                path_dic["input"],
                os.path.join(path_dic["workspace"], work),
                path_dic["backup"],
            )
            p.start()
            process.append(p)

        works = []
        new_works = workspace_m.regist_new_schedule(path_dic["backup"])
        if len(new_works) > 0:
            works = new_works

        tmp = []
        for p in process:
            if p.is_alive():
                tmp.append(p)
        process = tmp
        process_flag = True if len(process) > 0 else False

    for p in process:
        p.join()
    print("end")
