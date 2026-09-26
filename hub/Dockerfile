FROM quay.io/jupyterhub/jupyterhub:6.0.1

RUN python3 -m pip install --no-cache-dir \
        dockerspawner \
        jupyterhub-idle-culler

COPY jupyterhub_config.py /etc/jupyterhub/jupyterhub_config.py

WORKDIR /srv/jupyterhub
CMD ["jupyterhub", "-f", "/etc/jupyterhub/jupyterhub_config.py"]
