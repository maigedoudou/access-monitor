# 使用官方 Node.js 作为基础镜像
FROM node:18

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 yarn.lock
COPY package.json yarn.lock ./

# 清理缓存并重新安装依赖
RUN rm -rf node_modules && rm -f yarn.lock
RUN yarn install --frozen-lockfile --verbose

# 复制项目文件
COPY . .

# 开放容器端口
EXPOSE 3000

# 启动前端
CMD ["yarn", "dev"]



