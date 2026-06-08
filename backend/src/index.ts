import express from 'express'
import cors from 'cors'
import helmet from 'helmet'
import morgan from 'morgan'
import dotenv from 'dotenv'

import chatRoutes from './routes/chat'
import profileRoutes from './routes/profile'
import { errorHandler } from './middlewares/errorHandler'

dotenv.config()

const app = express()
const PORT = process.env.PORT || 3001

// 中间件
app.use(helmet())
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
}))
app.use(morgan('dev'))
app.use(express.json())

// 路由
app.use('/api/chat', chatRoutes)
app.use('/api/profile', profileRoutes)

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() })
})

// 错误处理
app.use(errorHandler)

// 启动服务器
app.listen(PORT, () => {
  console.log(`🦆 未来鹅后端服务运行在 http://localhost:${PORT}`)
})