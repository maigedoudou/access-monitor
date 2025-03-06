# SpyCo

Chill & Peace

intra-server-monitor/              # 根目录
│── backend/                       # 后端 (FastAPI)
│   │── main.py                     # FastAPI 主要代码
│   │── requirements.txt             # Python 依赖
│   │── Dockerfile                   # 后端 Docker 构建文件
│   └── __init__.py                   # 可能有的 Python 包文件
│
│── frontend/                       # 前端 (Vue 3 + Vite)
│   │── src/                         # Vue 源代码
│   │   │── components/              # Vue 组件
│   │   │   └── LogList.vue           # 日志列表组件
│   │   │── assets/                   # 静态资源 (图片, CSS)
│   │   │── App.vue                   # Vue 根组件
│   │   │── main.js                   # Vue 入口文件
│   │   └── index.html                # HTML 入口
│   │── public/                       # 公共静态资源
│   │── package.json                  # 前端依赖
│   │── yarn.lock                     # 依赖锁定文件
│   │── Dockerfile                    # 前端 Docker 构建文件
│   └── vite.config.js                 # Vite 配置文件
│
│── db_data/                         # MySQL 持久化存储
│
│── docker-compose.yml                # Docker Compose 配置文件
│── .dockerignore                      # Docker 忽略文件
│── README.md                
