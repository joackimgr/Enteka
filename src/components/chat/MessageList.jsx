import MessageBubble from "./MessageBubble"
import { useRef, useEffect } from "react"

export default function MessageList({ messages, typingUser }) {
    const bottomRef = useRef(null)

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" })
    }, [messages])

    let testMessages = messages.map(msg => <MessageBubble key={msg.id} text={msg.text} timestamp={msg.timestamp} isMine={msg.isMine} />)

    return (
        <div className="flex flex-col flex-1 overflow-y-auto min-h-0 bg-[#272B3D] px-2">
            {testMessages}
            {typingUser && (
                <div className="flex justify-start my-1.5">
                    <div className="bg-[#2F3347] px-4 py-3 rounded-2xl flex gap-1">
                        <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot" style={{ animationDelay: "0ms" }} />
                        <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot" style={{ animationDelay: "150ms" }} />
                        <span className="w-2 h-2 bg-gray-400 rounded-full typing-dot" style={{ animationDelay: "300ms" }} />
                    </div>
                </div>
            )}
            <div ref={bottomRef} />
        </div>
    )
}