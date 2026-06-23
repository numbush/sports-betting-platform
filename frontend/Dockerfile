# Stage 1 - Build React app
FROM node:20-alpine AS builder
# We use node:20-alpine as the base image - lightweight Node.js for building

# Set the working directory inside the container
WORKDIR /app

# Copy package files first (for better Docker layer caching)
# If dependencies didn't change, Docker skips the npm install step
COPY package*.json ./
RUN npm install

# Copy the rest of the source code
COPY . .

# Build the React app into static files (HTML, CSS, JS)
RUN npm run build

# Stage 2 - Serve with Nginx
# We throw away the Node.js image and start fresh with a tiny Nginx image
# This is called multi-stage build - final image has no Node.js, just static files
FROM nginx:alpine

# Copy only the built static files from Stage 1 into Nginx's serving directory
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/build /usr/share/nginx/html

# Tell Docker this container listens on port 80
EXPOSE 80

# Start Nginx in the foreground (daemon off = don't run as background process)
CMD ["nginx", "-g", "daemon off;"]