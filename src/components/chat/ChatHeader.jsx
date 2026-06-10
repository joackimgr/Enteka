import { CircleUserRound } from "lucide-react"

export default function ChatHeader() {

    return (
        <div className="flex justify-center items-center gap-5">
            <CircleUserRound size={50} alt="Profile" className="cursor-pointer text-white" />
            <h3 className="text-white">Test Username</h3>
        </div>
    )
}