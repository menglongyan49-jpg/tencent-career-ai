import React from 'react'
import { motion } from 'framer-motion'

interface GooseMascotProps {
  size?: number
  className?: string
  animate?: boolean
}

const GooseMascot: React.FC<GooseMascotProps> = ({
  size = 48,
  className = '',
  animate = true,
}) => {
  return (
    <motion.div
      className={`inline-flex items-center justify-center ${className}`}
      animate={animate ? { y: [0, -5, 0] } : undefined}
      transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* 身体 */}
        <ellipse cx="32" cy="40" rx="18" ry="16" fill="#FFE55C" />
        {/* 翅膀 */}
        <ellipse cx="16" cy="42" rx="6" ry="10" fill="#FFD93D" />
        <ellipse cx="48" cy="42" rx="6" ry="10" fill="#FFD93D" />
        {/* 头部 */}
        <circle cx="32" cy="22" r="14" fill="#FFE55C" />
        {/* 脸颊红晕 */}
        <circle cx="22" cy="24" r="4" fill="#FFB6B6" opacity="0.6" />
        <circle cx="42" cy="24" r="4" fill="#FFB6B6" opacity="0.6" />
        {/* 眼睛 */}
        <circle cx="27" cy="20" r="3" fill="#333" />
        <circle cx="37" cy="20" r="3" fill="#333" />
        <circle cx="28" cy="19" r="1" fill="white" />
        <circle cx="38" cy="19" r="1" fill="white" />
        {/* 嘴巴 */}
        <ellipse cx="32" cy="28" rx="4" ry="2.5" fill="#FF9F43" />
        {/* 头顶毛 */}
        <path
          d="M28 8 Q30 4 32 8 Q34 4 36 8"
          stroke="#FFD93D"
          strokeWidth="2"
          strokeLinecap="round"
        />
        {/* 领结 */}
        <path d="M28 34 L32 38 L36 34 L32 36 Z" fill="#54A0FF" />
      </svg>
    </motion.div>
  )
}

export default GooseMascot