### Stage 1: Build ###
# This Dockerfile uses Nginx to serve the static frontend files.

FROM nginx:1.25-alpine

# Copy the static content (HTML, CSS, JS) into the Nginx server directory
COPY . /usr/share/nginx/html

# Create writable temp directories used by NGINX on OpenShift
RUN mkdir -p /tmp/nginx/client_temp /tmp/nginx/proxy_temp /tmp/nginx/fastcgi_temp /tmp/nginx/uwsgi_temp /tmp/nginx/scgi_temp

# Use OpenShift-friendly NGINX configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose non-privileged port
EXPOSE 8080

# The default Nginx command will start the server.
# CMD ["nginx", "-g", "daemon off;"]