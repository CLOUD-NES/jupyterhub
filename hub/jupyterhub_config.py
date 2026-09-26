import os
import sys

c = get_config()  # noqa: F821

# --- Proxy: configurable-http-proxy runs as a separate compose service ---
c.ConfigurableHTTPProxy.should_start = False
c.ConfigurableHTTPProxy.api_url = "http://proxy:8001"
# The auth token is read from the CONFIGPROXY_AUTH_TOKEN environment variable.

# --- Hub networking ---
c.JupyterHub.hub_ip = "0.0.0.0"
c.JupyterHub.hub_port = 8081
c.JupyterHub.hub_connect_ip = "hub"

# --- Persistent hub state ---
c.JupyterHub.db_url = "sqlite:////srv/jupyterhub/jupyterhub.sqlite"
c.JupyterHub.cookie_secret_file = "/srv/jupyterhub/jupyterhub_cookie_secret"

# --- Authentication: one shared password for all participants ---
c.JupyterHub.authenticator_class = "shared-password"
c.SharedPasswordAuthenticator.user_password = os.environ["JUPYTERHUB_SHARED_PASSWORD"]
# Anyone who knows the shared password may log in with any username.
c.Authenticator.allow_all = True

admin_users = {
    u.strip() for u in os.environ.get("JUPYTERHUB_ADMIN_USERS", "").split(",") if u.strip()
}
admin_password = os.environ.get("JUPYTERHUB_ADMIN_PASSWORD", "")
if admin_users and admin_password:
    c.Authenticator.admin_users = admin_users
    c.SharedPasswordAuthenticator.admin_password = admin_password

# Usernames become directory names on the host: keep them simple.
c.Authenticator.username_pattern = r"^[a-z0-9][a-z0-9_.-]{0,31}$"

# --- Spawner: one JupyterLab container per user ---
c.JupyterHub.spawner_class = "docker"
c.DockerSpawner.image = os.environ.get("DOCKER_NOTEBOOK_IMAGE", "jupyter-singleuser:latest")
c.DockerSpawner.network_name = os.environ.get("DOCKER_NETWORK_NAME", "jupyterhub-network")
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.remove = True
c.DockerSpawner.mem_limit = os.environ.get("MEM_LIMIT", "2G")
c.DockerSpawner.cpu_limit = float(os.environ.get("CPU_LIMIT", "1"))

notebook_dir = "/home/jovyan"
c.DockerSpawner.notebook_dir = notebook_dir
user_storage_dir = os.environ.get("USER_STORAGE_DIR", "/data/storage/users")
c.DockerSpawner.volumes = {f"{user_storage_dir}/{{username}}": notebook_dir}
shared_dir = os.environ.get("SHARED_DIR", "/data/storage/shared")
c.DockerSpawner.read_only_volumes = {shared_dir: f"{notebook_dir}/shared"}

c.Spawner.default_url = "/lab"
c.Spawner.start_timeout = 120
c.Spawner.http_timeout = 60

# jovyan:users in the Jupyter Docker Stacks images
NB_UID, NB_GID = 1000, 100


def create_user_dirs(spawner):
    """Create the user's home directory on the host before spawning.

    Docker would otherwise create missing bind-mount sources owned by root,
    making the home directory read-only for the jovyan user.
    """
    for host_path in spawner.volume_binds:
        # Only the user homes are mounted in the hub container
        if not host_path.startswith(f"{user_storage_dir}/"):
            continue
        if not os.path.isdir(host_path):
            os.makedirs(host_path)
            os.chown(host_path, NB_UID, NB_GID)


c.Spawner.pre_spawn_hook = create_user_dirs

# --- Stop idle servers ---
c.JupyterHub.services = [
    {
        "name": "idle-culler",
        "command": [
            sys.executable,
            "-m",
            "jupyterhub_idle_culler",
            f"--timeout={os.environ.get('CULL_TIMEOUT', '3600')}",
        ],
    }
]
c.JupyterHub.load_roles = [
    {
        "name": "idle-culler",
        "scopes": [
            "list:users",
            "read:users:activity",
            "read:servers",
            "delete:servers",
        ],
        "services": ["idle-culler"],
    }
]
