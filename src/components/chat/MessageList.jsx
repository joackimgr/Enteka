import MessageBubble from "./MessageBubble"

export default function MessageList() {
    const messages = [
        {id: 1, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 2, text: "Whats up", timestamp: "12:35", isMine: false},
        {id: 3, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 4, text: "Whats up", timestamp: "12:35", isMine: false},
        {id: 5, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 6, text: "Whats up", timestamp: "12:35", isMine: false},
        {id: 7, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 8, text: "Whats up", timestamp: "12:35", isMine: false},
        {id: 9, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 10, text: "Whats up", timestamp: "12:35", isMine: false},
        {id: 11, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 12, text: "Whats up", timestamp: "12:35", isMine: false},
        {id: 1, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 2, text: "Whats up", timestamp: "12:35", isMine: false},
        {id: 3, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 4, text: "Whats up", timestamp: "12:35", isMine: false},
        {id: 5, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 6, text: "Whats up", timestamp: "12:35", isMine: false},
        {id: 7, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 8, text: "Whats up", timestamp: "12:35", isMine: false},
        {id: 9, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 10, text: "Whats up", timestamp: "12:35", isMine: false},
        {id: 11, text: "Hello",timestamp: "12:34", isMine: true},
        {id: 12, text: "Whats up", timestamp: "12:35", isMine: false}
    ]
    let testMessages = messages.map(msg => <MessageBubble key={msg.id} text={msg.text} timestamp={msg.timestamp} isMine={msg.isMine} />)

    return (
        <div className="flex flex-col flex-1 overflow-y-auto min-h-0 bg-[#272B3D] px-2">
            {testMessages}
        </div>
    )
}