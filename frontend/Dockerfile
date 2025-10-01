# Stage 1: Build the Vue.js application
FROM node:18-alpine AS build

WORKDIR /app

# Copy package.json and package-lock.json from the frontend directory
COPY frontend/package*.json ./

RUN npm install

# Copy the rest of the frontend application source code
COPY frontend/ . 

RUN npm run build

# Stage 2: Serve the static files with Nginx
FROM nginx:1.23-alpine

# Copy the built files from the build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Remove default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom Nginx configuration from the root nginx directory
COPY nginx/nginx.conf /etc/nginx/conf.d/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]