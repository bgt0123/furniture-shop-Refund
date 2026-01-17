# Simple frontend Dockerfile using existing build
FROM nginx:alpine

WORKDIR /usr/share/nginx/html

# Copy the already-built dist directory from the host
COPY dist/ .

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]