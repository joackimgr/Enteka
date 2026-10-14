import { useState } from "react"
import { Check, CheckCheck } from "lucide-react"
import { mediaUrl } from "../api/client"

export default function MessageBubble({text, timestamp, isMine, imageUrl, read}) {
    const [isOpen, setIsOpen] = useState(false)
    const src = mediaUrl(imageUrl)

    return (
        <>
            <div className={`flex ${isMine ? "justify-end" : "justify-start"} my-1.5`}>
                <div className={`${isMine ? "bg-[#7C6AF7]" : "bg-[#2F3347]"} px-4 py-2 rounded-2xl max-w-[70%] wrap-anywhere`}>
                    {src && (
                        <img
                            src={src}
                            alt="Sent image"
                            onClick={() => setIsOpen(true)}
                            className="rounded-xl max-w-full max-h-[300px] object-cover cursor-pointer"
                        />
                    )}
                    {text && <p className="text-white">{text}</p>}
                    <div className={`flex items-center gap-1 ${isMine ? "justify-end" : ""}`}>
                        <p className={`text-xs ${isMine ? "text-white/65" : "text-gray-400"}`}>{timestamp}</p>
                        {isMine && (read
                            ? <CheckCheck size={14} className="text-[#C7BFFF]" aria-label="Read" />
                            : <Check size={14} className="text-white/50" aria-label="Sent" />
                        )}
                    </div>
                </div>
            </div>
            {isOpen && src && (
                <div
                    className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8 cursor-zoom-out"
                    onClick={() => setIsOpen(false)}
                >
                    <img src={src} alt="Full size" className="max-h-full max-w-full rounded-xl" />
                </div>
            )}
        </>
    )
}
