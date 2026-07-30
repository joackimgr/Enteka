import logo from "../../assets/EntekaLogo.png"
import { Cog, CircleUserRound, Users } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'
import { useNavigate } from "react-router-dom"

export default function NavBar(props) {
    const [showDropdown, setShowDropdown] = useState(false)
    const navigate = useNavigate()
    const dropdownRef = useRef(null)

    function handleClick() {
        setShowDropdown(prev => !prev)
    }

    function handleLogout() {
        localStorage.removeItem("token")
        setShowDropdown(false)
        navigate('/')
    }

    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowDropdown(false)
            }
        }
        document.addEventListener('mousedown', handleClickOutside)
        return () => document.removeEventListener('mousedown', handleClickOutside)
    }, [])


    return (
        <nav className="flex items-center justify-between bg-[#272B3D] rounded-4xl mx-2.75 mt-2.75 mb-0 py-2.5 shrink-0">
            <div className="flex flex-row justify-center items-center gap-6.25 ml-6.25">
                <img src={logo} alt="EntekaLogo" id="appLogo" onClick={props.goHome} className="cursor-pointer w-12.5 h-12.5" />
                <p id="logoText" className="text-white text-[1.6rem]">ENTEKA</p>
            </div>
            <div className="flex flex-row justify-center items-center gap-6.25 mr-6.25">
                <Users size={45} alt='Friends' className="cursor-pointer" color="white" onClick={props.toggleFriendsMode}/>
                <Cog size={45} onClick={props.toggleChatMode} alt='Settings' className="cursor-pointer" color="white" />
                <div className="relative" ref={dropdownRef}>
                    <CircleUserRound size={45} alt="Profile" className="cursor-pointer" color="white" onClick={handleClick} />
                    {showDropdown && (
                        <div className="absolute top-full right-0 mt-2 bg-[#272B3D] rounded-xl shadow-lg z-50">
                            <button onClick={handleLogout} className="w-full px-4 py-2 text-left text-[#E05C5C] cursor-pointer hover:bg-[#363B52] transition-colors duration-150 rounded-xl whitespace-nowrap">
                                Log Out
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    )
}
