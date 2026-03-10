import { motion } from 'framer-motion'

export default function AILoader({ label = 'AI analyzing financial data...' }) {
  return (
    <div className="rounded-2xl border border-blue-200/70 bg-white/70 p-3 shadow-sm">
      <div className="flex items-center gap-3">
        <div className="relative h-8 w-8">
          <motion.span
            className="absolute inset-0 rounded-full bg-blue-400/30"
            animate={{ scale: [1, 1.35, 1], opacity: [0.6, 0.25, 0.6] }}
            transition={{ duration: 1.6, repeat: Infinity, ease: 'easeInOut' }}
          />
          <motion.span
            className="absolute inset-1 rounded-full bg-gradient-to-br from-blue-600 via-purple-600 to-emerald-500"
            animate={{ rotate: [0, 360] }}
            transition={{ duration: 1.4, repeat: Infinity, ease: 'linear' }}
          />
        </div>

        <div className="flex-1">
          <p className="text-sm font-semibold text-slate-800">{label} 🤖</p>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-200">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-blue-600 via-purple-600 to-emerald-500"
              animate={{ x: ['-50%', '100%'] }}
              transition={{ duration: 1.1, repeat: Infinity, ease: 'easeInOut' }}
              style={{ width: '55%' }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
