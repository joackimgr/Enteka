import logo from "../../assets/EntekaLogo.png"
import settings from "../../assets/settings_icon.png"
import profile from "../../assets/profile_icon.png"

export default function NavBar(props) {

    return (
        <nav className="flex items-center justify-between bg-[#272B3D] rounded-4xl mx-2.75 mt-2.75 mb-0 py-2.5 shrink-0">
            <div className="flex flex-row justify-center items-center gap-6.25 ml-6.25">
                <img src={logo} alt="EntekaLogo" id="appLogo" className="cursor-pointer w-12.5 h-12.5" />
                <p id="logoText" className="text-white text-[1.6rem]">ENTEKA</p>
            </div>
            <div className="flex flex-row justify-center items-center gap-6.25 mr-6.25">
                <img onClick={props.toggleChatMode} src={settings} alt="Settings" className="cursor-pointer w-12.5 h-12.5" />
                <img src={profile} alt="Profile" className="cursor-pointer w-11.25 h-11.25" />
            </div>
        </nav>
    )
}