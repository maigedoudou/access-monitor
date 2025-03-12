# FROM node:18

# WORKDIR /app

# COPY package.json yarn.lock ./

# RUN rm -rf node_modules && rm -f yarn.lock
# RUN yarn install --frozen-lockfile --verbose

# COPY . .

# EXPOSE 3000

# CMD ["yarn", "dev"]




# 使用更轻量的 Node.js 18 版本
FROM node:18-alpine  

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 yarn.lock
COPY package.json yarn.lock ./

# 安装依赖，确保 node_modules 只存在于容器中
RUN yarn install --frozen-lockfile --verbose

# 复制所有代码
COPY . .

# 指定 Vite 运行端口
EXPOSE 3000

# 运行 Vite 开发服务器
CMD ["yarn", "dev"]



