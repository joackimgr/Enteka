import { CircleUserRound, CircleArrowLeft } from "lucide-react"


export default function ChatHeader({username, handleBack}) {

    return (
        <div className="flex justify-center items-center gap-5 py-2 px-4 border-b border-[#40465D] bg-[#2F3347] relative">
            <CircleArrowLeft size={40} color="white" onClick={handleBack} className="absolute left-4 cursor-pointer transition-transform duration-150 ease-out hover:-translate-y-0.5"/>
            <CircleUserRound size={50} alt="Profile" className="cursor-pointer text-white" />
            <h3 className="text-white">{username}</h3>
        </div>
    )
}