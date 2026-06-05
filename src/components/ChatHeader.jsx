import profile from "../assets/profile_icon.png"

export default function ChatHeader() {

    return (
        <div className="flex justify-center items-center gap-5">
            <img src={profile} alt="user's profile pic" className="h-12.5 w-12.5"/>
            <h3 className="text-white">Test Username</h3>
        </div>
    )
}