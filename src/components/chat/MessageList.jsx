import MessageBubble from "./MessageBubble"

export default function MessageList({ messages }) {
    let testMessages = messages.map(msg => <MessageBubble key={msg.id} text={msg.text} timestamp={msg.timestamp} isMine={msg.isMine} />)

    return (
        <div className="flex flex-col flex-1 overflow-y-auto min-h-0 bg-[#272B3D] px-2">
            {testMessages}
        </div>
    )
}