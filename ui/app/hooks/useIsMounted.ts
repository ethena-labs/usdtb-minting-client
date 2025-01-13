import { useEffect, useState } from 'react'

export const useIsMounted = (duration = 500) => {
  const [isMounted, setIsMounted] = useState(false)

  useEffect(() => {
    setTimeout(() => {
      setIsMounted(true)
    }, duration)
  }, [duration])

  return isMounted
}
