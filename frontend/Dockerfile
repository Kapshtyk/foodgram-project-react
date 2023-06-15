# build env
FROM node:13.12.0-alpine as build
WORKDIR /app
RUN pwd
COPY ./frontend/ /app/frontend/
RUN pwd
WORKDIR /app/frontend
RUN pwd
RUN npm install
RUN npm run build
CMD cp -r build result_build
RUN ls -la
