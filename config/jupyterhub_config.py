import sys

c = get_config()

# The docker instances need access to the Hub, so the default loopback port doesn't work:
from jupyter_client.localinterfaces import public_ips
c.JupyterHub.hub_ip = public_ips()[0]

c.JupyterHub.services = [
    {
        'name': 'idle-culler',
        'admin': True,
        'command': [
            sys.executable,
            '-m',
            'jupyterhub_idle_culler',
            # Servers that have been idle for longer then timeout (in seconds) will be culled.
            '--timeout=86400', # 1 day
            # The maximum age (in seconds) of servers that should be culled even if they are active.
            '--max_age=604800', # 7 days
        ],
    }
]

c.JupyterHub.bind_url = 'https://127.0.0.1:8000'
c.JupyterHub.port = 8000

# Don't interrupt users when jupyterhub service is restarted
c.JupyterHub.cleanup_servers = False
c.JupyterHub.cleanup_proxy = False

# Delete any users from the database that do not pass validation
c.Authenticator.delete_invalid_users = True

# Users who successfully authenticate are allowed in
c.Authenticator.allow_all = True

# Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
c.Application.log_level = 'DEBUG'

c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'

# replace with your desired image see https://github.com/jupyter/docker-stacks/tree/main/images
c.DockerSpawner.image = 'ghcr.io/cloud-nes/jupyter:latest'

# Default access point
c.Spawner.default_url = '/lab?reset'

# set c.Spawner.cmd to launch singleuser server with jupyterlab
c.Spawner.cmd = ['jupyter-labhub']

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
# On SRC, the scratch directory should be mounted and not /home directory
# default mode is  "mode": "rw"
c.DockerSpawner.volumes = {
    "/scratch": {"bind": "/home/jovyan/scratch"},
    "/data": {"bind": "/home/jovyan/data"}
}

# Delete containers when servers are stopped. This will destroy any data in the
# container not stored in mounted volumes. Default is False, that means when the
# server is stopped by the user, the container status is Exited(0) i.e. stopped.
# In this case, the container is not deleted, but it is not running too. If the
# user starts the server again, the same container is re-started and therefore
# data and packages installed are preserved. If the user closes the browser
# without stopping the server, the container will continue running.
# c.DockerSpawner.remove = True

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True
