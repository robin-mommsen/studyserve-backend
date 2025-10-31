from infra.Terraform.ansibler import Ansibler

def start(
        server_id,
        world_id,
        server,
        action,
        vm_type
):
    ansible = Ansibler(server_id, world_id, power_script)
    ansible.start(vm_type)

    return server, server_id, action

def shutdown(
        server_id,
        world_id,
        server,
        action,
        vm_type
):
    ansible = Ansibler(server_id, world_id, power_script)
    ansible.shutdown(vm_type)

    return server, server_id, action

def stop(
        server_id,
        world_id,
        server,
        action,
        vm_type
):
    ansible = Ansibler(server_id, world_id, power_script)
    ansible.stop(vm_type)

    return server, server_id, action

power_script="""
- name: VM starten (falls nötig) und IP releasen
  hosts: localhost
  connection: local
  vars:
    api_auth: "{{ lookup('env', 'ANSIBLE_AUTH') }}"
    type: "{{ 'qemu' if vm == 'server' else ('lxc' if vm == 'container' else 'unbekannt') }}"
    api_url: "https://vpn.hv01.studyserve.de:8006/api2/json/nodes/studyserve-hv"

  tasks:
    - name: start VM
      uri:
        url: "{{api_url}}/{{ type }}/{{ vmid }}/status/start"
        method: POST
        headers:
          Authorization: "{{api_auth}}"
        validate_certs: no
      when: mode == "start"

    - name: shutdown VM
      uri:
        url: "{{api_url}}/{{ type }}/{{ vmid }}/status/shutdown"
        method: POST
        headers:
          Authorization: "{{api_auth}}"
        validate_certs: no
      when: mode == "shutdown"

    - name: stop VM
      uri:
        url: "{{api_url}}/{{ type }}/{{ vmid }}/status/stop"
        method: POST
        headers:
          Authorization: "{{api_auth}}"
        validate_certs: no
      when: mode == "stop"
"""