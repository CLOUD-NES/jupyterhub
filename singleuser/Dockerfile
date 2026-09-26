# Keep the hub-X.Y.Z tag in sync with the hub image version (hub/Dockerfile)
FROM quay.io/jupyter/scipy-notebook:hub-6.0.1

COPY --chown=${NB_UID}:${NB_GID} environment.yml /tmp/environment.yml
RUN mamba env update --name base --file /tmp/environment.yml && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
