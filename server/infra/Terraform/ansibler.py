import os.path
import re
import subprocess
from pathlib import Path

class AnsibleError(Exception):
    pass

class Ansibler:

    def __init__(self,server_id, world_id, ansible_file, path = "/app/server/ansible/"):
        print("Initializing ansibler.\n")
        tmp_path = os.path.realpath(path)
        self.__world_id = world_id
        self.__ansible_path = os.path.join(tmp_path, str(server_id))
        os.makedirs(self.__ansible_path, exist_ok=True)
        self.__ansible_file = ansible_file
        self.create_ansible_file()


    def create_ansible_file(self):
        new_ansible_file = open(os.path.join(self.__ansible_path, "ansible.yml"), "w")
        new_ansible_file.write(self.__ansible_file)
        new_ansible_file.close()


    def run_ansible_command(self, command):
        print(f"command: {' '.join(command)}")
        try:
            result = subprocess.run(
                ["ansible-playbook"] + command + ["ansible.yml"],
                cwd=self.__ansible_path,
                text=True,
                capture_output=True,
                check=True,
                encoding="utf-8"
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {' '.join(command)}")
            print(e.stderr)
            raise AnsibleError(f"Ansible command failed: {e.stderr}")


    def start(self, vm_type):
        self.run_ansible_command(["-e", f"vmid={self.__world_id} mode=start vm={vm_type}"])
        self.delete_project()

    def stop(self, vm_type):
        self.run_ansible_command(["-e", f"vmid={self.__world_id} mode=stop vm={vm_type}"])
        self.delete_project()

    def shutdown(self, vm_type):
        self.run_ansible_command(["-e", f"vmid={self.__world_id} mode=shutdown vm={vm_type}"])
        self.delete_project()

    def create_container(self, ip_address, sub_domain_name):
        output = self.run_ansible_command(["-e", f"ip_address={ip_address} kunde={sub_domain_name}"])
        match = re.search(r'domain_name:\s*(https?://[^\s"]+)', output)
        if match:
            domain = match.group(1)
        else:
            raise AnsibleError("Failed to extract domain name from Ansible output.")

        return domain

    def delete_project(self):
        print("\n ##################################### \n")
        print("Deleting the project...\n")
        def rmdir(directory):
            directory = Path(directory)
            for item in directory.iterdir():
                if item.is_dir():
                    rmdir(item)
                else:
                    item.unlink()
            directory.rmdir()
        rmdir(self.__ansible_path)
        print("Project deleted.\n")