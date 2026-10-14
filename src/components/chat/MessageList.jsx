import MessageBubble from "./MessageBubble"
import { useRef, useEffect, useLayoutEffect } from "react"

const NEAR_BOTTOM_PX = 40

export default function MessageList({ messages, typingUser }) {
    const containerRef = useRef(null)
    const contentRef = useRef(null)
    const pinnedRef = useRef(true)
    const isFirstRef = useRef(true)

    function scrollToBottom(behavior) {
        const el = containerRef.current
        if (el) el.scrollTo({ top: el.scrollHeight, behavior })
    }

    function handleScroll() {
        const el = containerRef.current
        if (!el) return
        pinnedRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < NEAR_BOTTOM_PX
    }

    // Instant on the first render (chat open), smooth after (new message / typing).
    useLayoutEffect(() => {
        scrollToBottom(isFirstRef.current ? "auto" : "smooth")
        isFirstRef.current = false
    }, [messages, typingUser])

    // Re-pin when content height changes after the fact (images decoding, etc).
    useEffect(() => {
        const content = contentRef.current
        if (!content || typeof ResizeObserver === "undefined") return
        const observer = new ResizeObserver(() => {
            if (pinnedRef.current) scrollToBottom("auto")
        })
        observer.observe(content)
        return () => observer.disconnect()
    }, [])

    let testMessages = messages.map(msg => <MessageBubble key={msg.id} text={msg.text} timestamp={msg.timestamp} isMine={msg.isMine} imageUrl={msg.image_url} read={msg.read} />)

    return (
        <div ref={containerRef} onScroll={handleScroll} className="flex flex-col flex-1 overflow-y-auto min-h-0 bg-[#272B3D] px-2">
            <div ref={contentRef}>
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
            </div>
        </div>
    )
}
