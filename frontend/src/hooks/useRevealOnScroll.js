import { useAnimation, useInView } from 'framer-motion'
import { useEffect, useRef } from 'react'

export default function useRevealOnScroll({ once = true, margin = '-15% 0px -15% 0px' } = {}) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once, margin })
  const controls = useAnimation()

  useEffect(() => {
    if (isInView) {
      controls.start('visible')
    }
  }, [controls, isInView])

  return { ref, controls, isInView }
}
