import { Frown, CircleUserRound } from "lucide-react"

export default function Sidebar(props) {

    return (
        <>
            {props.chatMode &&
                <div className="flex flex-col justify-center items-center bg-[#272B3D] rounded-4xl text-white">
                    <Frown size={70} alt="Sad Emoji"/>
                    <p className="text-white">You have no chats yet.</p>
                </div>
            }
            {!props.chatMode && 
                <div className="bg-[#272B3D] rounded-[1.2rem] p-2.75 flex flex-col items-center gap-2.75">
                    <div onClick={props.toggleStatus} className="bg-[#40465d] mb-2.75 p-2.75 w-full box-border rounded-[1.2rem] flex items-center gap-5 cursor-pointer hover:bg-[#3a3f54] transition-colors duration-100 ease-in">
                        <CircleUserRound size={50} alt="Account Settings Icon" className="text-white"/>
                        <p className="text-white text-[23px] font-light m-0">Account Settings</p>
                    </div>
                </div>
            }
        </>
    )
}