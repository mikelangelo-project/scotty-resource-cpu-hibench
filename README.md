Stressor Resource Deployment
===================

[![N|Solid](https://www.gwdg.de/GWDG-Theme-1.0-SNAPSHOT/images/gwdg_logo.svg)](https://nodesource.com/products/nsolid)

## Overview
Here the resource for workload-stressor is created using a heat stack.

### Prerequisite
1. pip install -r requirement.txt
2. Modify OpenStack credential ( Make sure the account you are using has enough quota )

### Output
a dictioinary is the output of this resource which contains:
* `ip`: IP address of the endpoint
* `user`: User of the endpoint
* `private_key`: Private key of the endpoint


#### Notes
* The `experiment_name` used to tag the data when it is later stored on MongoDB as metadata, thus it should be identical to the experiment name in resource component `experiment_name`.

Sample configuration for experiment.yaml
```yaml
resources:
  - name: resource_stressor
    generator: file:resource/stressor
    params:
      experiment_name: "csws_experiment"
      OpenStack_auth_url: OPENSTACK_AUTH_URL
      OpenStack_username: OPENSTACK_USERNAME
      OpenStack_password: OPENSTACK_PASSWORD
      OpenStack_tenant_name: OPENSTACK_TENANT_NAME
      OpenStack_project_name: OPENSTACK_PROJECT_NAME
      tag: "stressor1"
      stressor_flavor: "kvm.m1.large"
```
