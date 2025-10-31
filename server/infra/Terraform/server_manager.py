from infra.Terraform.terraformer import Terraformer
from .vm_types import Vm

def create_server_terraform(
        hostname,
        server,
        server_id,
        tf_script,
        ssh_key,
        base_dir="/app/server/tfprojects/"
    ):

    tf = Terraformer(base_dir, server_id, tf_script, Vm.SERVER)

    tf.format()
    tf.validate_syntax()

    if tf.syntax_is_valid():
        tf.plan(hostname, ssh_key)
        tf.apply(hostname, ssh_key)
        ip_address, root_password, world_id = tf.output()
    else:
        raise ValueError("Terraform syntax is not valid. Cannot create server.")

    tf.delete_project()

    return server, ip_address, root_password, world_id

def delete_server_terraform(
        server,
        server_id,
        tf_script,
        reason,
        base_dir="/app/server/tfprojects/"
    ):
    tf = Terraformer(base_dir, server_id, tf_script, Vm.SERVER)

    tf.destroy()
    tf.delete_project()

    return server, reason

