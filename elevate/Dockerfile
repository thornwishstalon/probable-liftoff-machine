# build stage
FROM node:16-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install --silent \
    npm install @vue/cli -g

COPY babel.config.js ./
COPY . .
RUN npm run build


#prod build
FROM bitnami/apache:latest
COPY --from=build-stage /app/dist /app
