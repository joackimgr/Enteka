import ChatHeader from "./ChatHeader";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import { useState, useEffect } from "react";
import { getMessages, sendMessages } from "../api/client";

export default function ChatView({selectedChat, handleBack, bumpChatRefresh}) {
    const [messages, setMessages] = useState([])
    const [loading, setLoading] = useState(true)

    async function addMessage(text) {
       const result = await sendMessages(selectedChat.chat_id, text)
       if (result && result.auth) {
        const data = await getMessages(selectedChat.chat_id)
        if (data && data.auth) {
            setMessages(data.messages.map(m => ({
                id: m.id,
                text: m.content,
                timestamp: m.timestamp,
                isMine: m.is_mine
            })))
        } 
        if (bumpChatRefresh) bumpChatRefresh()
       }
    }

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
                <MessageList messages={messages}/>
            )}
            <MessageInput SendMessage={addMessage}/>
        </div>
    )
}