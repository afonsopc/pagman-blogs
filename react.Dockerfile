# Build the website

FROM node:latest AS build-website

WORKDIR /app

COPY . .

RUN npm install
RUN npm audit fix
RUN npm run build


# Serve the website

FROM busybox:1.36

# Create a non-root user to own the files and the server
RUN adduser -D static
USER static
WORKDIR /home/static

# Copy the static website
COPY --from=build-website /app/dist .

# Run BusyBox httpd
CMD echo "starting http server..." && busybox httpd -f -v -p 3000