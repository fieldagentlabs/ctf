# Field Agents lab image: one container with Juice Shop (CTF mode), Python,
# Claude Code, and the control CLI's runtime. Since v2 (Season 1) it also has the
# nginx front, a K7 canary listener, the pinned Juice Shop source, and tsc for
# deploy-shop.
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
ARG NODE_TOOLS_IMAGE=node:24.22.2-trixie-slim@sha256:0820eaa85e07d0490446dd01d14707e17e6108a36988cf374899cd057eb3812d

FROM ${JUICE_SHOP_IMAGE} AS shop

# TypeScript compiler for deploy-shop, pinned to the version Juice Shop builds with.
FROM ${NODE_TOOLS_IMAGE} AS tools
RUN npm install -g --prefix /opt/tools typescript@6.0.3

FROM ${BASE_IMAGE}

ARG CLAUDE_CODE_VERSION=2.1.323
ARG CTF_KEY
RUN test -n "${CTF_KEY}" || (echo "Build argument CTF_KEY is required." >&2 && exit 1)

# Node and Juice Shop come straight from the official image, so the Node
# version always matches what Juice Shop was built with.
COPY --from=shop /nodejs /opt/nodejs
COPY --from=shop --chown=vscode:vscode /juice-shop /opt/juice-shop
RUN ln -s /opt/nodejs/bin/node /usr/local/bin/node && node --version

# A pristine copy of the server source: init-juice-shop-src copies it into the
# workspace, and deploy-shop --original restores from it.
RUN mkdir /opt/juice-shop-src \
    && cd /opt/juice-shop \
    && tar --exclude=./node_modules --exclude=./build --exclude=./frontend/dist --exclude=./logs \
           --exclude='./data/*.sqlite' --exclude=./uploads -cf - . | tar -xf - -C /opt/juice-shop-src \
    && chown -R vscode:vscode /opt/juice-shop-src

COPY --from=tools /opt/tools /opt/tools
RUN ln -s /opt/tools/bin/tsc /usr/local/bin/tsc && tsc --version

# nginx front (Season 1): logs bodies in the breach log's format and 404s unknown paths.
RUN apt-get update && apt-get install -y --no-install-recommends nginx \
    && rm -rf /var/lib/apt/lists/* /etc/nginx/sites-enabled/default \
    && mkdir -p /var/log/shop && chmod 755 /var/log/shop
COPY nginx-shop.conf /etc/nginx/conf.d/shop.conf
COPY gen-dist-locations.py /tmp/gen-dist-locations.py
RUN python3 /tmp/gen-dist-locations.py /opt/juice-shop/frontend/dist/frontend /etc/nginx/fieldagents-dist.conf \
    && rm /tmp/gen-dist-locations.py && nginx -t

# Grader dependencies (pinned): pySigma for K5; the Claude API SDK and Agent SDK for P1 to P5.
COPY requirements-graders.txt /tmp/requirements-graders.txt
RUN pip install --no-cache-dir -r /tmp/requirements-graders.txt && rm /tmp/requirements-graders.txt \
    && python3 -c "import sigma.matching, anthropic, claude_agent_sdk, importlib.metadata as m; print('pySigma', m.version('pySigma'), 'anthropic', m.version('anthropic'), 'claude-agent-sdk', m.version('claude-agent-sdk'))"

COPY start-shop.sh /usr/local/bin/start-shop
COPY restart-shop.sh /usr/local/bin/restart-shop
COPY deploy-shop.sh /usr/local/bin/deploy-shop
COPY init-juice-shop-src.sh /usr/local/bin/init-juice-shop-src
COPY canary.py /usr/local/bin/canary
RUN chmod 755 /usr/local/bin/start-shop /usr/local/bin/restart-shop /usr/local/bin/deploy-shop \
              /usr/local/bin/init-juice-shop-src /usr/local/bin/canary

ENV NODE_ENV=ctf \
    CTF_KEY=${CTF_KEY} \
    SHOP_URL=http://localhost:3000 \
    JUICE_SHOP_SRC=/workspaces/juice-shop \
    PATH=/home/vscode/.local/bin:${PATH}

USER vscode
RUN curl -fsSL https://claude.ai/install.sh | bash -s ${CLAUDE_CODE_VERSION} \
    && claude --version

LABEL org.opencontainers.image.title="fa-lab" \
      org.opencontainers.image.description="Field Agents lab: Juice Shop in CTF mode plus Claude Code" \
      org.opencontainers.image.source="https://github.com/fieldagentlabs/ctf"
