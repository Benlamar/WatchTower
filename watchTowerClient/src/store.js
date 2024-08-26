import { configureStore } from "@reduxjs/toolkit";
import authSlice from "./slices/authSlice";
import streamSlice from "./slices/streamSlice";

export const store = configureStore({
    reducer: {
        auth: authSlice,
        stream: streamSlice
    }
});