import { Cog, X } from "lucide-react"
import { getMe, updateUsername, updateEmail, updatePassword } from "../api/client"
import { useState, useEffect } from "react"

export default function SettingsPanel(props) {
    const [modal, setModal] = useState(null)
    const [usernameInput, setUsernameInput] = useState("")
    const [emailInput, setEmailInput] = useState("")
    const [currentPassword, setCurrentPassword] = useState("")
    const [newPassword, setNewPassword] = useState("")
    const [errorMessage, setErrorMessage] = useState("")
    const [profile, setProfile] = useState(null)

    useEffect(() => {
        async function fetchProfile() {
            const data = await getMe()
            if (data && data.auth && data.profile) {
                setProfile(data.profile)
            }
        }
        fetchProfile()
    }, [])

    const options = ["username", "password", "email"]

    function openModal(option) {
        setModal(option)
        if (option === 'username' && profile) setUsernameInput(profile.username)
        if (option === 'email' && profile) setEmailInput(profile.email)
        setErrorMessage("")
    }

    const optionsItems = options.map((i) => {
        return (
            <div key={i} onClick={() => openModal(i)} className="bg-[#2F3347] rounded-[1.2rem] p-5 box-border h-auto text-3xl w-full flex justify-center cursor-pointer hover:bg-[#363B52] transition-colors duration-100 ease-in">
                <p className="text-white m-0 font-light">{`Change your ${i}.`}</p>
            </div>
        )
    })

    async function handleUsernameSubmit(e) {
        e.preventDefault()
        const data = await updateUsername(usernameInput)
        if (data.auth) {
            localStorage.setItem("token", data.token)
            props.setUserName(data.username)
            setProfile(prev => ({ ...prev, username: data.username }))
            setErrorMessage("")
            setUsernameInput("")
            setModal(null)
        } else {
            setErrorMessage(data.message || "Something went wrong.")
        }
    }

    async function handleEmailSubmit(e) {
        e.preventDefault()
        const data = await updateEmail(emailInput)
        if (data.auth) {
            setProfile(prev => ({ ...prev, email: data.email }))
            setErrorMessage("")
            setEmailInput("")
            setModal(null)
        } else {
            setErrorMessage(data.message || "Something went wrong.")
        }
    }

    async function handlePasswordSubmit(e) {
        e.preventDefault()
        const data = await updatePassword(currentPassword, newPassword)
        if (data.auth) {
            setErrorMessage("")
            setCurrentPassword("")
            setNewPassword("")
            setModal(null)
        } else {
            setErrorMessage(data.message || "Something went wrong.")
        }
    }


    return (
        <>
            {!props.activeSettings && 
                <div className="flex items-center justify-center">
                    <Cog size={200} alt="Settings Icon" className="text-white"/>
                </div>
            }
            {props.activeSettings && 
                <div className="bg-[#272B3D] rounded-[1.2rem] p-2.75 flex flex-col items-center gap-2.75">
                    {optionsItems}
                    <div className="bg-[#2F3347] rounded-[1.2rem] p-5 box-border h-auto text-3xl w-full flex justify-center opacity-50 cursor-not-allowed">
                        <p className="text-white m-0 font-light">Change your profile picture. <span className="text-sm text-[#9B9DB8]">(coming soon)</span></p>
                    </div>
                </div>
            }
            {modal === 'username' &&
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setModal(null)}>
                    <form onSubmit={handleUsernameSubmit} onClick={(e) => e.stopPropagation()} className="bg-[#272B3D] rounded-[1.2rem] p-6 flex flex-col gap-4 w-96">
                        <div className="flex justify-between items-center">
                            <h2 className="text-white text-xl font-light m-0">Change your username</h2>
                            <X size={20} color="white" className="cursor-pointer" onClick={() => setModal(null)} />
                        </div>
                        <input
                            type="text"
                            value={usernameInput}
                            onChange={(e) => setUsernameInput(e.target.value)}
                            placeholder="New username"
                            className="bg-[#2F3347] text-white rounded-[1.1rem] px-4 py-2 outline-none focus:ring-2 focus:ring-[#7C6AF7]"
                            required
                        />
                        {errorMessage && <p className="text-red-400 text-sm m-0">{errorMessage}</p>}
                        <button type="submit" className="bg-[#7C6AF7] hover:bg-[#6A59E0] text-white rounded-xl py-2 cursor-pointer transition-colors duration-100">
                            Save
                        </button>
                    </form>
                </div>
            }
            {modal === 'email' &&
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setModal(null)}>
                    <form onSubmit={handleEmailSubmit} onClick={(e) => e.stopPropagation()} className="bg-[#272B3D] rounded-[1.2rem] p-6 flex flex-col gap-4 w-96">
                        <div className="flex justify-between items-center">
                            <h2 className="text-white text-xl font-light m-0">Change your email</h2>
                            <X size={20} color="white" className="cursor-pointer" onClick={() => setModal(null)} />
                        </div>
                        <input
                            type="email"
                            value={emailInput}
                            onChange={(e) => setEmailInput(e.target.value)}
                            placeholder="New email"
                            className="bg-[#2F3347] text-white rounded-[1.1rem] px-4 py-2 outline-none focus:ring-2 focus:ring-[#7C6AF7]"
                            required
                        />
                        {errorMessage && <p className="text-red-400 text-sm m-0">{errorMessage}</p>}
                        <button type="submit" className="bg-[#7C6AF7] hover:bg-[#6A59E0] text-white rounded-xl py-2 cursor-pointer transition-colors duration-100">
                            Save
                        </button>
                    </form>
                </div>
            }
            {modal === 'password' &&
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setModal(null)}>
                    <form onSubmit={handlePasswordSubmit} onClick={(e) => e.stopPropagation()} className="bg-[#272B3D] rounded-[1.2rem] p-6 flex flex-col gap-4 w-96">
                        <div className="flex justify-between items-center">
                            <h2 className="text-white text-xl font-light m-0">Change your password</h2>
                            <X size={20} color="white" className="cursor-pointer" onClick={() => setModal(null)} />
                        </div>
                        <input
                            type="password"
                            value={currentPassword}
                            onChange={(e) => setCurrentPassword(e.target.value)}
                            placeholder="Current password"
                            className="bg-[#2F3347] text-white rounded-[1.1rem] px-4 py-2 outline-none focus:ring-2 focus:ring-[#7C6AF7]"
                            required
                        />
                        <input
                            type="password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            placeholder="New password"
                            className="bg-[#2F3347] text-white rounded-[1.1rem] px-4 py-2 outline-none focus:ring-2 focus:ring-[#7C6AF7]"
                            required
                        />
                        {errorMessage && <p className="text-red-400 text-sm m-0">{errorMessage}</p>}
                        <button type="submit" className="bg-[#7C6AF7] hover:bg-[#6A59E0] text-white rounded-xl py-2 cursor-pointer transition-colors duration-100">
                            Save
                        </button>
                    </form>
                </div>
            }
        </>
    )
}