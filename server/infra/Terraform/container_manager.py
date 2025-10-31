from infra.Terraform.terraformer import Terraformer
from infra.Terraform.ansibler import Ansibler
from .vm_types import Vm

def create_container(
        hostname,
        service,
        service_id,
        tf_script,
        ansible_script,
        ssh_key,
        base_dir="/app/container/tfprojects/"
):

    tf = Terraformer(base_dir, service_id, tf_script, Vm.CONTAINER)

    tf.format()
    tf.validate_syntax()

    if tf.syntax_is_valid():
        tf.plan_container(hostname)
        tf.apply_container(hostname)
        ip_address, root_password, world_id = tf.output()
    else:
        raise ValueError("Terraform syntax is not valid. Cannot create container.")

    tf.delete_project()


    ansible = Ansibler(service_id, world_id, ansible_script)
    domain = ansible.create_container(ip_address, hostname)

    return service, ip_address, root_password, domain, world_id

def delete_container(
        service,
        service_id,
        hostname,
        tf_script,
        reason,
        base_dir="/app/container/tfprojects/"
):
    tf = Terraformer(base_dir, service_id, tf_script, Vm.CONTAINER)

    tf.destroy_container(hostname)
    tf.delete_project()

    return service, reason
