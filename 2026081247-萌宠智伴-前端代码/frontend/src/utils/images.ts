export const DEFAULT_STUDENT_AVATAR = '/images/avatars/stu.jpg'
export const DEFAULT_PET_IMAGE = '/images/pets/dog1.jpg'

export function setImageFallback(event: Event, fallback: string) {
  const image = event.target as HTMLImageElement
  image.onerror = null
  image.src = fallback
}
