import ChatHeader from "./ChatHeader";
import MessageList from "./MessageList";
import MessageInput from "./MessageInput";

export default function ChatView() {

    return (
        <div className="flex flex-col h-full min-h-0 flex-1 overflow-hidden rounded-4xl bg-[#272B3D]">
            <ChatHeader />
            <MessageList />
            <MessageInput />
        </div>
    )
}