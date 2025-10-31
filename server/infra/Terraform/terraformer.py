import os
import re
from pathlib import Path
import subprocess
from .vm_types import Vm


class TerraformError(Exception):
    pass

class Terraformer:
    __validSyntax = False
    __isPlanned = False


    def __init__(self, terraform_base_dir, server_id, tfFile, vm_type: Vm):
        print("Initializing terraformer.\n")
        self.__terraform_base_dir = os.path.realpath(terraform_base_dir)
        prefix = "s" if vm_type == Vm.SERVER else "c"
        self.__serverID = prefix + str(server_id)
        self.__terraformProjectPath = os.path.join(self.__terraform_base_dir, self.__serverID)
        self.__tfFile = tfFile
        print("Terraform base dir: " + self.__terraform_base_dir)
        print("Server ID: " + self.__serverID)
        print("Project path: " + self.__terraformProjectPath)
        os.makedirs(self.__terraformProjectPath, exist_ok=True)
        self.create_tf_file()
        self.init()


    def create_tf_file(self):
        newTfFile = open(os.path.join(self.__terraformProjectPath, "main.tf"), "w")
        newTfFile.write(self.__tfFile)
        newTfFile.close()


    def run_terraform_command(self, command):
        print(f"command: {' '.join(command)}")
        try:
            result = subprocess.run(
                ["terraform"] + command,
                cwd=self.__terraformProjectPath,
                text=True,
                capture_output=True,
                check=True,
                encoding="utf-8"
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {' '.join(command)}")
            print(e.stderr)
            raise TerraformError(f"Terraform command failed: {e.stderr}")


    def init(self):
        print("\n ##################################### \n")
        print("Initializing terraform project...\n")
        output = self.run_terraform_command(["init"])
        if output:
            print(output)
        workspaceOutput = self.run_terraform_command(["workspace", "select", "-or-create", self.__serverID])
        if workspaceOutput:
            print(workspaceOutput)


    def format(self):
        print("\n ##################################### \n")
        print("Formatting .tf files...\n")
        output = self.run_terraform_command(["fmt"])
        if output:
            print('Formatted following files: \n' + output)


    def validate_syntax(self):
        print("\n ##################################### \n")
        print("Validating Syntax...\n")
        output = self.run_terraform_command(["validate"])
        if output and "Success!" in output:
            print('Validation status: valid')
            self.__validSyntax = True
        else:
            print(output)


    def plan(self, hostname, ssh_key):
        print("\n ##################################### \n")
        print("Planning the infrastructure...\n")
        try:
            output = self.run_terraform_command(["plan", "-var", f"hostname={hostname}", "-var", f"root_ssh_key={ssh_key}"])
            if output:
                self.__isPlanned = True
                print(output)
        except TerraformError as e:
            print(f"Planning failed: {e}")
            raise


    def apply(self, hostname, ssh_key):
        print("\n ##################################### \n")
        if not self.__validSyntax:
            raise TerraformError("Syntax is not valid. Cannot apply.")
        elif not self.__isPlanned:
            raise TerraformError("Please run plan before applying.")
        else:
            print("Applying the infrastructure...\n")
            try:
                output = self.run_terraform_command(["apply", "-var", f"hostname={hostname}", "-var", f"root_ssh_key={ssh_key}", "-auto-approve"])
                if output:
                    print(output)
            except TerraformError as e:
                print(f"Apply failed: {e}")
                raise


    def destroy(self):
        print("\n ##################################### \n")
        self.__isPlanned = False
        self.__validSyntax = False
        print("Destroying the infrastructure...\n")
        try:
            output = self.run_terraform_command(["destroy", "-var", f"hostname=", "-var", f"root_ssh_key=", "-auto-approve"])
            if output:
                print(output)
        except TerraformError as e:
            print(f"Destroy failed: {e}")
            raise


    def plan_container(self, hostname):
        print("\n ##################################### \n")
        print("Planning the infrastructure...\n")
        try:
            output = self.run_terraform_command(["plan", "-var", f"hostname={hostname}"])
            if output:
                self.__isPlanned = True
                print(output)
        except TerraformError as e:
            print(f"Planning failed: {e}")
            raise


    def apply_container(self, hostname):
        print("\n ##################################### \n")
        if not self.__validSyntax:
            raise TerraformError("Syntax is not valid. Cannot apply.")
        elif not self.__isPlanned:
            raise TerraformError("Please run plan before applying.")
        else:
            print("Applying the infrastructure...\n")
            try:
                output = self.run_terraform_command(["apply", "-var", f"hostname={hostname}", "-auto-approve"])
                if output:
                    print(output)
            except TerraformError as e:
                print(f"Apply failed: {e}")
                raise


    def destroy_container(self, hostname):
        print("\n ##################################### \n")
        self.__isPlanned = False
        self.__validSyntax = False
        print("Destroying the infrastructure...\n")
        try:
            output = self.run_terraform_command(["destroy", "-var", f"hostname={hostname}", "-auto-approve"])
            if output:
                print(output)
        except TerraformError as e:
            print(f"Destroy failed: {e}")
            raise


    def output(self):
        print("\n ##################################### \n")
        print("Defined outputs")
        try:
            output = self.run_terraform_command(["output"])
            if output:
                print(output)
                ip_match = re.search(r'vm_ip\s*=\s*"(\d{1,3}(?:\.\d{1,3}){3})"', output)
                ip_address = ip_match.group(1) if ip_match else None

                world_id_match = re.search(r'world_id\s*=\s*(\d+)', output)
                world_id = world_id_match.group(1) if world_id_match else None

                password_match = re.search(r'root_password\s*=\s*"([^"]*)"', output)
                root_password = password_match.group(1) if password_match else None

                return ip_address, root_password, world_id

        except TerraformError as e:
            print(f"Output retrieval failed: {e}")
            raise


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
        rmdir(self.__terraformProjectPath)
        print("Project deleted.\n")


    def syntax_is_valid(self):
        return self.__validSyntax
