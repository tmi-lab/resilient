# STAGE: Install dependencies
FROM node:18.18.2-alpine3.18 as Deps

WORKDIR /app
COPY ./resilient_frontend/package*.json ./
RUN npm install

# STAGE: Build Front End
FROM node:18.18.2-alpine3.18 as Build
WORKDIR /app
COPY --from=Deps /app/node_modules ./node_modules
COPY ./resilient_frontend .
COPY ./resilient_frontend/*.json .

RUN npm run build

# Stage 2: Serve the application with Nginx
FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*

COPY ./docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=Build /app/dist/resilient_frontend /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
