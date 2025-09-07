### Stage 1: Build ###
# This Dockerfile uses Nginx to serve the static frontend files.

FROM nginx:1.25-alpine

# Copy the static content (HTML, CSS, JS) into the Nginx server directory
COPY . /usr/share/nginx/html

RUN chown -R nginx:nginx /var/cache/nginx

# Copy the Nginx configuration file
# This is optional for this simple case, but good practice.
# We will create a simple config to handle API proxying if needed.
# For now, we will assume the API is exposed on the same host or we'll handle it at the ingress/route level.
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# The default Nginx command will start the server.
# CMD ["nginx", "-g", "daemon off;"]