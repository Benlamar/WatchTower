import "./App.css";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard/Dashboard";
import Login from "./components/Login/Login";
import Layout from "./components/Layout";
import ProtectedRoutes from "./components/ProtectedRoutes/ProtectedRoutes";

function App() {
  return (
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route path="/login" element={<Login />} />

          <Route element={<ProtectedRoutes/>}>
            <Route path="/" element={<Dashboard />} />
          </Route>
          
        </Route>
      </Routes>
  );
}

export default App;
