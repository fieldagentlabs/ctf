# Field Agents lab image: one container with Juice Shop (CTF mode), Python,
# Claude Code, and the control CLI's runtime.
#
# Published as ghcr.io/fieldagentlabs/fa-lab by a workflow in the private
# ctf-hq repo, which passes the real CTF_KEY as a build argument. That key is
# baked into the image on purpose (decision D1, honor system): it is never in
# git, but anyone who inspects the image can read it.
#
# Local build with your own throwaway key:
#   docker build --platform linux/amd64 --build-arg CTF_KEY=dev-only \
#     -t fa-lab:dev .devcontainer/image

# Pinned by tag and digest. Juice Shop v20.4.0 runs on Node 24 over Debian 13,
# so the workspace base is Debian 13 (trixie) too, for its native modules.
ARG JUICE_SHOP_IMAGE=bkimminich/juice-shop:v20.4.0@sha256:9bbaecc41791f00b002bc65931cc5ff355fbdb941fa72b06558c18dace43197b
ARG BASE_IMAGE=mcr.microsoft.com/devcontainers/python:3.3.4-3.12-trixie@sha256:4c12f5b63120240d923320ddc16fb8a386d4a5e35236f3d0b6e5c2c170355041

FROM ${JUICE_SHOP_IMAGE} AS shop

FROM ${BASE_IMAGE}

ARG CLAUDE_CODE_VERSION=2.1.323
ARG CTF_KEY
RUN test -n "${CTF_KEY}" || (echo "Build argument CTF_KEY is required." >&2 && exit 1)

# Node and Juice Shop come straight from the official image, so the Node
# version always matches what Juice Shop was built with.
COPY --from=shop /nodejs /opt/nodejs
COPY --from=shop --chown=vscode:vscode /juice-shop /opt/juice-shop
RUN ln -s /opt/nodejs/bin/node /usr/local/bin/node && node --version

COPY start-shop.sh /usr/local/bin/start-shop
RUN chmod 755 /usr/local/bin/start-shop

ENV NODE_ENV=ctf \
    CTF_KEY=${CTF_KEY} \
    SHOP_URL=http://localhost:3000 \
    PATH=/home/vscode/.local/bin:${PATH}

USER vscode
RUN curl -fsSL https://claude.ai/install.sh | bash -s ${CLAUDE_CODE_VERSION} \
    && claude --version

LABEL org.opencontainers.image.title="fa-lab" \
      org.opencontainers.image.description="Field Agents lab: Juice Shop in CTF mode plus Claude Code" \
      org.opencontainers.image.source="https://github.com/fieldagentlabs/ctf"
