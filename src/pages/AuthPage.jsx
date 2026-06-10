import { useState } from "react"
import LoginForm from "../components/auth/LoginForm"
import SignUpForm from "../components/auth/SignUpForm"

export default function AuthPage(props) {
    const [showSignUp, setShowSignUp] = useState(false)

    function toggleSwitch() {
        setShowSignUp(prevState => !prevState)
    }

    return (
        <section className="bg-[#272B3D] h-full rounded-4xl flex-1 flex flex-col items-center justify-center min-h-150">
            {showSignUp
                ? <SignUpForm onSwitch = {toggleSwitch} setIsAuthenticated={props.setIsAuthenticated} setUserName={props.setUserName} />
                : <LoginForm onSwitch = {toggleSwitch} setIsAuthenticated={props.setIsAuthenticated} setUserName={props.setUserName} />
            }
        </section>
    )
}