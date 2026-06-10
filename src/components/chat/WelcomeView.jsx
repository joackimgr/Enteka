import profile from "../../assets/profile_icon.png"

export default function WelcomeView(props) {

    return (
        <div className="flex flex-col justify-center items-center bg-[#272B3D] rounded-4xl gap-8">
            <img src={profile} alt="Profile Icon" className="w-42.5 h-42.5"/>
            <p className="text-[50px] box-border leading-[0.3] text-white font-light">{`Hello, ${props.userName}!`}</p>
            <button onClick={props.turnOffWelcomeMode} className="border-0 bg-[#646A84] text-white w-auto h-12.5 text-3xl rounded-2xl py-0 px-2.75 font-light cursor-pointer hover:bg-[#5c627b] transition-colors duration-100">Start a new chat!</button>
        </div>
    )
}