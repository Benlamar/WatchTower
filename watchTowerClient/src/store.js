import { configureStore, combineReducers } from "@reduxjs/toolkit";
import authSlice from "./slices/authSlice";
import streamSlice from "./slices/streamSlice";
import { persistStore, persistReducer, FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER } from 'redux-persist';
// import { persistStore, persistReducer } from 'redux-persist'
import storage from 'redux-persist/lib/storage';
import { version } from "react";

const persistConfig = {
    key : 'root',
    version: 1,
    storage,
    whitelist: ['auth', 'stream']
};

const rootReducer = combineReducers({
    auth: authSlice,
    stream: streamSlice
})

const persistedReducerAS = persistReducer(persistConfig, rootReducer);

const store = configureStore({
    // reducer: {
    //     auth: persistedReducerAuth,
    //     stream: streamSlice
    // }
    reducer: persistedReducerAS,
    middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
});

const persistor = persistStore(store);

export {store, persistor};