import { CircleUserRound } from "lucide-react"

export default function ChatHeader() {

    return (
        <div className="flex justify-center items-center gap-5 py-2 px-4 border-b border-[#40465D] bg-[#2F3347]">
            <CircleUserRound size={50} alt="Profile" className="cursor-pointer text-white" />
            <h3 className="text-white">Test Username</h3>
        </div>
    )
}