from hibench.resource import HiBenchResource


HiBenchResource.reduce_logging()

def deploy(context):
    hibench_resource = HiBenchResource(context)
    endpoint = hibench_resource.deploy()
    return endpoint

def clean(context):
    hibench_resource = HiBenchResource(context)
    hibench_resource.clean() 
