import logo from "../../assets/EntekaLogo.png"
import { useState } from "react"
import { useNavigate } from "react-router-dom";
import { signUpDataPython } from "../api/client"

export default function SignUpForm({onSwitch, setIsAuthenticated, setUserName}) {
    let navigate = useNavigate()

    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: ''
    });

    const [errorMessage, setErrorMessage] = useState('')

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({
            ...prevState,
            [name]: value
        }));
    };

    async function handleSubmit(e) {
        e.preventDefault()
        let data = await signUpDataPython(formData)
        if (data.auth) {
            setErrorMessage("")
            setIsAuthenticated(true)
            setUserName(formData.username)
            localStorage.setItem("token", data.token)
            navigate("/home")
        }
        else {
            setErrorMessage(data.message)
        }
        }

    return <form onSubmit={handleSubmit} id="signUpForm" className="flex flex-col bg-[#272B3D] justify-center items-center w-112.5 h-auto my-5 mx-auto rounded-[1.6rem] gap-4">
                <img src={logo} alt="EntekaLogo" width={120} height={120} id="logoOnSignUpForm" className="mt-6"/>
                
                <label htmlFor="signUpUsername" className="text-2xl text-[#F0F0F5]">Username</label>
                <input value={formData.username} onChange={handleChange} type="text" name="username" id="signUpUsername" className="w-62.5 text-[#F0F0F5] border-none rounded-[1.1rem] h-9.25 bg-[#2F3347] p-0 box-border focus:outline-none pl-3.5 focus:box-border" required />
                
                <label htmlFor="signUpEmail" className="text-2xl text-[#F0F0F5]">Email</label>
                <input value={formData.email} onChange={handleChange} type="email" name="email" id="signUpEmail" className="w-62.5 text-[#F0F0F5] border-none rounded-[1.1rem] h-9.25 bg-[#2F3347] p-0 box-border focus:outline-none pl-3.5 focus:box-border" required />
                
                <label htmlFor="signUpPassword" className="text-2xl text-[#F0F0F5]">Password</label>
                <input value={formData.password} onChange={handleChange} type="password" name="password" id="signUpPassword" className="w-62.5 text-[#F0F0F5] border-none rounded-[1.1rem] h-9.25 bg-[#2F3347] p-0 box-border focus:outline-none pl-3.5 focus:box-border" required />
                {errorMessage &&
                    <p className="text-red-400 text-sm">{errorMessage}</p>
                }
                <p className="my-2.5 text-xl text-[#F0F0F5]">Already have an account? <span id="logIn" onClick={onSwitch} className="cursor-pointer text-[#7C6AF7]">Log In!</span></p>
                
                <input type="submit" value="Sign Up!" id="signUpBtn" className="w-30 h-12.5 text-xl border-none rounded-[1.2rem] bg-[#7C6AF7] mb-4.5 cursor-pointer transition-colors hover:bg-[#6A59E0]"/>
            </form>

}