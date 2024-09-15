import React, { useEffect } from "react";
import { useSelector } from "react-redux";
import { Navigate, Outlet } from "react-router-dom";

const ProtectedRoutes = () => {
  const authTokenSelector = useSelector((state) => state.auth.accessToken);
  const authSelector = useSelector((state) => state.auth.auth);

  useEffect(()=>{
    console.log(authSelector,"---",authTokenSelector)
  },[authSelector, authTokenSelector])

  return authSelector && authTokenSelector ? (
    <Outlet />
  ) : (
    <Navigate to="/login" replace />
  );
};

export default ProtectedRoutes;
