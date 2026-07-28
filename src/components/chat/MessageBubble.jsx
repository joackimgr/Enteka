export default function MessageBubble({text, timestamp, isMine}) {

    return (
        <div className={`flex ${isMine ? "justify-end" : "justify-start"} my-1.5`}>
            <div className={`${isMine ? "bg-[#7C6AF7]" : "bg-[#2F3347]"} px-4 py-2 rounded-2xl max-w-[70%] break-words`}>
                <p className="text-white">{text}</p>
                <p className={`text-xs ${isMine ? "text-white/65" : "text-gray-400"}`}>{timestamp}</p>
            </div>
        </div>
    )
}