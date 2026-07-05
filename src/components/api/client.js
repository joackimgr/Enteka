import axios from 'axios';

export const loginDataPython = async (data) => {
    try {
        const response = await axios.post('http://localhost:8000/login', {
            username: data.username,
            password: data.password
        });
        console.log('Data sent successfully:', response.data);
        return response.data
    } catch (error) {
        console.error('Error sending data:', error);
        return { auth: false, message: 'Network error. Try again.' }
    }
}

export const signUpDataPython = async (data) => {
    try {
        const response = await axios.post('http://localhost:8000/signup', {
            username: data.username,
            email: data.email,
            password: data.password
        });
        console.log('Data sent successfully:', response.data);
        return response.data
    } catch (error) {
        console.error('Error sending data:', error);
        return { auth: false, message: 'Network error. Try again.' }
    }
}

export const verifyToken = async (token) => {
    try {
        const response = await axios.post('http://localhost:8000/verify', {
            token: token
        })
        return response.data
    } catch (error) {
        console.error('Error verifying token', error)
        return {auth: false, message: 'Network error. Try again.'}
    }
}