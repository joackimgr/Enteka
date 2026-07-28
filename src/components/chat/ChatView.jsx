import ChatHeader from "./ChatHeader";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import { useState, useEffect, useRef } from "react";
import { getMessages, WS_BASE } from "../api/client";

export default function ChatView({selectedChat, handleBack, bumpChatRefresh, userName}) {
    const [messages, setMessages] = useState([])
    const [loading, setLoading] = useState(true)
    const [typingUser, setTypingUser] = useState(null)
    const wsRef = useRef(null)
    const typingTimerRef = useRef(null)
    const isIntentionalCloseRef = useRef(false)
    const reconnectAttemptRef = useRef(0)
    const reconnectTimerRef = useRef(null)
    

    function addMessage(text) {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: "message", content: text }))
            wsRef.current.send(JSON.stringify({ type: "stop_typing" }))
        }
       if (typingTimerRef.current) clearTimeout(typingTimerRef.current)
    }

    function handleTyping() {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: "typing"}))
        }
        if (typingTimerRef.current) clearTimeout(typingTimerRef.current)
        
        typingTimerRef.current = setTimeout(() => {
            if (wsRef.current?.readyState === WebSocket.OPEN) {
                wsRef.current.send(JSON.stringify({ type: "stop_typing" }))
            }
        }, 1000)
    }

    function connect() {
        const token = localStorage.getItem('token')
        const wsUri = `${WS_BASE}/ws/${selectedChat.chat_id}?token=${token}`
        const websocket = new WebSocket(wsUri)
        wsRef.current = websocket

        websocket.onopen = () => {
            reconnectAttemptRef.current = 0
        }

        websocket.onmessage = (event) => {
            const data = JSON.parse(event.data)
            if (data.type === "new_message") {
                const isMine = data.username === userName
                setMessages(prev => [...prev, {
                    id: data.message_id,
                    text: data.content,
                    timestamp: data.timestamp,
                    isMine: isMine
                }])
                if (bumpChatRefresh) bumpChatRefresh()
            } else if (data.type === "typing") {
                setTypingUser(data.username)
            } else if (data.type === "stop_typing") {
                setTypingUser(prev => prev === data.username ? null : prev)
            }
        }

        websocket.onerror = (event) => {
            console.error(`${event}`)
        }

        websocket.onclose = () => {
            if (!isIntentionalCloseRef.current) {
                const max_attempts = 5
                if (reconnectAttemptRef.current < max_attempts) {
                    const delay = 1000 * (2 ** reconnectAttemptRef.current)
                    reconnectAttemptRef.current += 1
                    reconnectTimerRef.current = setTimeout(() => {
                        connect()
                    }, delay)
                }
            }
        }
    }

    useEffect(() => {
        isIntentionalCloseRef.current = false
        connect()
        return () => {
            isIntentionalCloseRef.current = true
            if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current)
            wsRef.current.close()
            if (typingTimerRef.current) clearTimeout(typingTimerRef.current)
        }
    }, [selectedChat.chat_id])

    useEffect(() => {
        async function fetchMessages() {
            setLoading(true)
            const data = await getMessages(selectedChat.chat_id)
            if (data && data.auth) {
                setMessages(data.messages.map(m => ({
                    id: m.id,
                    text: m.content,
                    timestamp: m.timestamp,
                    isMine: m.is_mine
                })))
            }
            setLoading(false)
        }
        fetchMessages()
    }, [selectedChat.chat_id])

    return (
        <div className="flex flex-col h-full min-h-0 flex-1 overflow-hidden rounded-4xl bg-[#272B3D]">
            <ChatHeader username={selectedChat.username} handleBack={handleBack} />
            {loading ? (
                <div className="flex items-center justify-center flex-1 text-white">Loading messages...</div>
            ) : (
                <MessageList messages={messages} typingUser={typingUser} />
            )}
            <MessageInput SendMessage={addMessage} onTyping={handleTyping} />
        </div>
    )
}