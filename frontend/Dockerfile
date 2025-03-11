FROM node:18

WORKDIR /app

COPY package.json yarn.lock ./

RUN rm -rf node_modules && rm -f yarn.lock
RUN yarn install --frozen-lockfile --verbose

COPY . .

EXPOSE 3000

CMD ["yarn", "dev"]



