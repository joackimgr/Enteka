import { CircleUserRound } from "lucide-react"
import { mediaUrl } from "./api/client"

export default function Avatar({ src, size = 45, className = "", ...rest }) {
    const url = mediaUrl(src)
    if (url) {
        return (
            <img
                src={url}
                alt="Profile"
                style={{ width: size, height: size }}
                className={`rounded-full object-cover shrink-0 ${className}`}
                {...rest}
            />
        )
    }
    return <CircleUserRound size={size} color="white" className={`shrink-0 ${className}`} {...rest} />
}
