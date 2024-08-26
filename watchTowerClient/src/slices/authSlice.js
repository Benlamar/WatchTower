import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    user: "",
    auth: "",
    role: "",
    accessToken: null
};

export const authSlice = createSlice({
    name: "auth",
    initialState,
    reducers: {
        setAuth: (state, action) => {
            state.user = action.payload.user
            state.auth = action.payload.auth
            state.role = action.payload.role
            state.accessToken = action.payload.accessToken
        }
    }
});

export const { setAuth } = authSlice.actions
export default authSlice.reducer