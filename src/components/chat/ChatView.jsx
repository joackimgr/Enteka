import ChatHeader from "./ChatHeader";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";
import { useState } from "react";

export default function ChatView({selectedChat}) {
    const [messages, setMessages] = useState([
        {id: 1, text: "Hello",timestamp: "12:34", isMine: false}
    ])

    function addMessage(text) {
        const newMessage = {
            id: Date.now(),
            text: text,
            timestamp: new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', hour12: false}),
            isMine: true
        }
        setMessages(prev => [...prev, newMessage])
    }

    return (
        <div className="flex flex-col h-full min-h-0 flex-1 overflow-hidden rounded-4xl bg-[#272B3D]">
            <ChatHeader username={selectedChat.username}/>
            <MessageList messages={messages}/>
            <MessageInput SendMessage={addMessage}/>
        </div>
    )
}