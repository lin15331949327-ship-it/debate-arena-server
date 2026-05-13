FROM node:18-slim

# Install Python 3.11 + symlink
RUN apt-get update && apt-get install -y python3.11 python3-pip --no-install-recommends && \
    ln -sf /usr/bin/python3.11 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Node dependencies
COPY package*.json ./
RUN npm ci --omit=dev

# Python dependencies
COPY requirements.txt ./
RUN pip3 install --break-system-packages -r requirements.txt

# App code
COPY . .

# Expose port
EXPOSE 3001

# Start
CMD ["node", "index.js"]
# force rebuild 2026-05-12 v2
